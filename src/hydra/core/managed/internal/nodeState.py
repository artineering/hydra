
"""Node status enumeration for the Hydra managed services system."""

from enum import Enum


class NodeState(Enum):
    """Enumeration representing the various states a managed node can be in.
    
    This enum is used throughout the Hydra system to track and manage the
    lifecycle states of individual nodes in the distributed system.
    """
    
    UNINITIALIZED = 0  # Node has been created but not yet configured
    INITIALIZED = 1    # Node is configured and ready to start
    RUNNING = 2        # Node is actively running and processing
    STOPPED = 3        # Node has been gracefully stopped
    ERROR = 4          # Node has encountered an error and is in a failed state