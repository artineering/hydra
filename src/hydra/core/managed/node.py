import subprocess
import logging
from datetime import datetime
from typing import List, Optional

from .internal.nodeConfig import NodeConfig
from .internal.nodeState import NodeState
from .internal.nodeRuntimeState import NodeRuntimeState


class ManagedNode:
    def __init__(self, config: NodeConfig):
        self.config: NodeConfig = config
        self.state: NodeRuntimeState = NodeRuntimeState(name=config.name)
        self.logger = logging.getLogger(config.name)
    
    def _prepareCommand(self) -> List[str]:
        """Prepare the ROS2 command to launch the node."""
        cmd = ["ros2", "run", self.config.package, self.config.executable]
        
        # Add ROS args if we have parameters or remappings
        if self.config.parameters or self.config.remappings or self.config.namespace != "/":
            cmd.append("--ros-args")
            
            # Add namespace
            if self.config.namespace and self.config.namespace != "/":
                cmd.extend(["-r", f"__ns:={self.config.namespace}"])
            
            # Add parameter remappings
            for old_name, new_name in self.config.remappings.items():
                cmd.extend(["-r", f"{old_name}:={new_name}"])
            
            # Add parameters
            for param_name, param_value in self.config.parameters.items():
                cmd.extend(["-p", f"{param_name}:={param_value}"])
        
        return cmd
        
    def start(self) -> bool:
        """Start the managed node process."""
        try:
            # Check if already running
            if self.state.process and self.state.process.poll() is None:
                self.logger.warning(f"Node {self.config.name} is already running!")
                return False
            
            # Check if node is enabled
            if not self.config.enabled:
                self.logger.info(f"Node {self.config.name} is disabled, skipping start")
                return False
            
            # Prepare command
            cmd = self._prepareCommand()
            self.logger.info(f"Starting node {self.config.name} with command: {' '.join(cmd)}")
            
            # Start the process
            self.state.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Update state
            self.state.pid = self.state.process.pid
            self.state.start_time = datetime.now()
            self.state.state = NodeState.RUNNING
            self.state.last_error = None
            
            self.logger.info(f"Node {self.config.name} started successfully with PID {self.state.pid}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to start node {self.config.name}: {str(e)}"
            self.logger.error(error_msg)
            self.state.state = NodeState.ERROR
            self.state.last_error = error_msg
            return False
    
    def stop(self, timeout: float = 10.0) -> bool:
        """Stop the managed node process gracefully."""
        try:
            # Check if process exists and is running
            if not self.state.process:
                self.logger.warning(f"Node {self.config.name} is not running (no process)")
                return True
            
            if self.state.process.poll() is not None:
                self.logger.info(f"Node {self.config.name} is already stopped")
                self.state.state = NodeState.STOPPED
                return True
            
            self.logger.info(f"Stopping node {self.config.name} (PID: {self.state.pid})")
            
            # First try graceful termination
            self.state.process.terminate()
            
            try:
                # Wait for graceful shutdown
                self.state.process.wait(timeout=timeout)
                self.logger.info(f"Node {self.config.name} stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                self.logger.warning(f"Node {self.config.name} did not stop gracefully, force killing")
                self.state.process.kill()
                self.state.process.wait()
                self.logger.info(f"Node {self.config.name} force stopped")
            
            # Update state
            self.state.state = NodeState.STOPPED
            self.state.pid = None
            self.state.last_error = None
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to stop node {self.config.name}: {str(e)}"
            self.logger.error(error_msg)
            self.state.state = NodeState.ERROR
            self.state.last_error = error_msg
            return False
    
    def is_running(self) -> bool:
        """Check if the node process is currently running.
        
        Returns:
            bool: True if the process exists and is running, False otherwise
        """
        return (self.state.process is not None and 
                self.state.process.poll() is None)
    
    def get_status(self) -> dict:
        """Get comprehensive status information about the node.
        
        Returns:
            dict: Status information including:
                - name: Node name
                - state: Current NodeState
                - pid: Process ID (if running)
                - start_time: When the node was started
                - restart_count: Number of restarts
                - last_error: Last error message (if any)
                - enabled: Whether the node is enabled
                - running: Whether the process is currently active
        """
        return {
            'name': self.config.name,
            'state': self.state.state.name,
            'pid': self.state.pid,
            'start_time': self.state.start_time.isoformat() if self.state.start_time else None,
            'restart_count': self.state.restart_count,
            'last_error': self.state.last_error,
            'enabled': self.config.enabled,
            'running': self.is_running()
        }
