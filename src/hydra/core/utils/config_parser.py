"""
Configuration parser for Hydra node management system.

This module provides functionality to parse YAML configuration files and convert
them into NodeConfig objects for the Hydra system.
"""

import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..managed.internal.nodeConfig import NodeConfig
from ..managed.internal.nodeState import NodeState


class ConfigurationParser:
    """
    Parser for Hydra configuration files that converts YAML configuration
    into NodeConfig objects.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_file(self, config_path: str) -> List[NodeConfig]:
        """
        Parse a YAML configuration file and return a list of NodeConfig objects.
        
        Args:
            config_path (str): Path to the YAML configuration file
            
        Returns:
            List[NodeConfig]: List of configured nodes
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            yaml.YAMLError: If the YAML file is malformed
            ValueError: If required configuration fields are missing
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_file, 'r') as file:
                config_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse YAML file {config_path}: {e}")
            raise
        
        return self.parse_config(config_data)
    
    def parse_config(self, config_data: Dict[str, Any]) -> List[NodeConfig]:
        """
        Parse configuration dictionary and return NodeConfig objects.
        
        Args:
            config_data (Dict[str, Any]): Configuration dictionary from YAML
            
        Returns:
            List[NodeConfig]: List of configured nodes
            
        Raises:
            ValueError: If required configuration fields are missing
        """
        if not config_data:
            self.logger.warning("Empty configuration provided")
            return []
        
        nodes_config = config_data.get('nodes', [])
        if not nodes_config:
            self.logger.warning("No nodes found in configuration")
            return []
        
        node_configs = []
        for i, node_data in enumerate(nodes_config):
            try:
                node_config = self._parse_node(node_data)
                node_configs.append(node_config)
                self.logger.debug(f"Parsed node configuration: {node_config.name}")
            except Exception as e:
                self.logger.error(f"Failed to parse node {i}: {e}")
                raise ValueError(f"Invalid node configuration at index {i}: {e}")
        
        self.logger.info(f"Successfully parsed {len(node_configs)} node configurations")
        return node_configs
    
    def _parse_node(self, node_data: Dict[str, Any]) -> NodeConfig:
        """
        Parse individual node configuration data.
        
        Args:
            node_data (Dict[str, Any]): Node configuration dictionary
            
        Returns:
            NodeConfig: Configured node object
            
        Raises:
            KeyError: If required fields are missing
            ValueError: If field values are invalid
        """
        # Validate required fields
        required_fields = ['name', 'package', 'executable']
        for field in required_fields:
            if field not in node_data:
                raise KeyError(f"Required field '{field}' missing from node configuration")
        
        # Extract basic configuration
        name = str(node_data['name'])
        package = str(node_data['package'])
        executable = str(node_data['executable'])
        
        # Extract optional fields with defaults
        namespace = str(node_data.get('namespace', '/'))
        enabled = bool(node_data.get('enabled', True))
        auto_restart = bool(node_data.get('auto_restart', True))
        respawn_delay = float(node_data.get('respawn_delay', 2.0))
        
        # Extract remappings and parameters
        remappings = self._parse_remappings(node_data.get('remappings', {}))
        parameters = self._parse_parameters(node_data.get('parameters', {}))
        
        return NodeConfig(
            name=name,
            package=package,
            executable=executable,
            namespace=namespace,
            remappings=remappings,
            parameters=parameters,
            state=NodeState.UNINITIALIZED,
            enabled=enabled,
            auto_restart=auto_restart,
            respawn_delay=respawn_delay
        )
    
    def _parse_remappings(self, remappings_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Parse and validate remappings configuration.
        
        Args:
            remappings_data (Dict[str, Any]): Remappings from configuration
            
        Returns:
            Dict[str, str]: Validated remappings dictionary
        """
        if not isinstance(remappings_data, dict):
            self.logger.warning("Remappings must be a dictionary, using empty dict")
            return {}
        
        remappings = {}
        for key, value in remappings_data.items():
            remappings[str(key)] = str(value)
        
        return remappings
    
    def _parse_parameters(self, parameters_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate parameters configuration.
        
        Args:
            parameters_data (Dict[str, Any]): Parameters from configuration
            
        Returns:
            Dict[str, Any]: Validated parameters dictionary
        """
        if not isinstance(parameters_data, dict):
            self.logger.warning("Parameters must be a dictionary, using empty dict")
            return {}
        
        return dict(parameters_data)
    
    def get_system_config(self, config_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract system-level configuration from the config data.
        
        Args:
            config_data (Dict[str, Any]): Full configuration dictionary
            
        Returns:
            Optional[Dict[str, Any]]: System configuration or None if not present
        """
        return config_data.get('system')