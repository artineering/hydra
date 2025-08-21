"""
NodeConfig is a data class that encapsulates the configuration for a node within the system.

Attributes:
    packageName (str): The name of the package containing the node. Defaults to an empty string.
    nodeName (str): The name of the node. Defaults to an empty string.
    paramFileName (str): The filename of the parameter file associated with the node. Defaults to an empty string.
    remappings (Dict): A dictionary specifying topic or service remappings for the node. Defaults to an empty dictionary.
    parameters (Dict): A dictionary containing parameter names and their corresponding values for the node. Defaults to an empty dictionary.
    status (NodeStatus): The current status of the node, represented by the NodeStatus enum. Defaults to NodeStatus.UNINITIALIZED.
"""

from dataclasses import dataclass
from typing import Dict
from .nodeState import NodeState

@dataclass
class NodeConfig:
    package: str
    name: str
    executable: str
    namespace: str = "/"
    remappings: Dict(str, str) = {}
    parameters: Dict(str, any) = {}
    state: NodeState = NodeState.UNINITIALIZED
    enabled: bool = True
    auto_restart: bool = True
    respawn_delay: float = 2.0