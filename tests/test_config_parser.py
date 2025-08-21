#!/usr/bin/env python3
"""
Test script for the ConfigurationParser class.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hydra.core.utils.config_parser import ConfigurationParser

def main():
    parser = ConfigurationParser()
    
    # Test parsing the example configuration
    config_path = "src/hydra/config/configuration.yaml"
    
    try:
        node_configs = parser.parse_file(config_path)
        
        print(f"Successfully parsed {len(node_configs)} nodes:")
        print("-" * 50)
        
        for config in node_configs:
            print(f"Name: {config.name}")
            print(f"Package: {config.package}")
            print(f"Executable: {config.executable}")
            print(f"Namespace: {config.namespace}")
            print(f"Enabled: {config.enabled}")
            print(f"Auto-restart: {config.auto_restart}")
            print(f"Respawn delay: {config.respawn_delay}")
            print(f"Parameters: {config.parameters}")
            print(f"Remappings: {config.remappings}")
            print(f"State: {config.state}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error parsing configuration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())