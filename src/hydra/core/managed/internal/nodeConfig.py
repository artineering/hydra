"""
NodeConfig is a data class that encapsulates the configuration for a node within the system.

Attributes:
    package (str): The name of the ROS2 package containing the node.
    name (str): The name of the node instance.
    executable (str): The executable name within the package.
    launch_file (str, optional): The launch file name within the package. If provided, uses 'ros2 launch' instead of 'ros2 run'.
    namespace (str): The ROS2 namespace for the node. Defaults to "/".
    remappings (Dict[str, str]): A dictionary specifying topic or service remappings for the node. Defaults to an empty dictionary.
    parameters (Dict[str, Any]): A dictionary containing parameter names and their corresponding values for the node. Defaults to an empty dictionary.
    state (NodeState): The current status of the node, represented by the NodeState enum. Defaults to NodeState.UNINITIALIZED.
    enabled (bool): Whether the node should be started when the system launches. Defaults to True.
    auto_restart (bool): Whether the node should be automatically restarted if it fails. Defaults to True.
    respawn_delay (float): The delay in seconds before restarting a failed node. Defaults to 2.0.
    use_terminal (bool): Whether the node should be launched in a separate terminal window. Defaults to False.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .nodeState import NodeState

@dataclass
class NodeConfig:
    package: str
    name: str
    executable: str
    launch_file: Optional[str] = None
    namespace: str = "/"
    remappings: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    state: NodeState = NodeState.UNINITIALIZED
    enabled: bool = True
    auto_restart: bool = True
    respawn_delay: float = 2.0
    use_terminal: bool = False