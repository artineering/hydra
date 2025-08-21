import subprocess
import logging
import tempfile
import os
from datetime import datetime
from typing import List

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
    
    def _start_in_terminal(self, cmd: List[str]) -> bool:
        """Start the node in a separate terminal window."""
        try:
            ros2_command = " ".join(cmd)
            
            # Create a script to run in the terminal
            script_content = f"""#!/bin/bash
echo "Starting {self.config.name}..."
echo "Command: {ros2_command}"
echo "Press Ctrl+C to stop this node, or close terminal to exit"
echo "----------------------------------------"

# Function to handle cleanup when terminal is closed
cleanup() {{
    echo ""
    echo "Node {self.config.name} is stopping..."
    # Kill any background processes if they exist
    jobs -p | xargs -r kill 2>/dev/null
    exit 0
}}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Run the ROS2 command
{ros2_command} &
ROS_PID=$!

# Wait for the ROS process to complete
wait $ROS_PID
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "Node {self.config.name} completed successfully."
else
    echo "Node {self.config.name} exited with code $EXIT_CODE."
fi
echo "Press Enter to close this terminal..."
read
"""
            
            # Write script to temporary file
            
            script_fd, script_path = tempfile.mkstemp(suffix=f"_hydra_{self.config.name}.sh", text=True)
            try:
                with os.fdopen(script_fd, 'w') as f:
                    f.write(script_content)
                os.chmod(script_path, 0o755)
                
                # Launch in new terminal (try different terminal emulators)
                terminal_commands = [
                    # GNOME Terminal
                    ["gnome-terminal", "--", "bash", script_path],
                    # xterm
                    ["xterm", "-e", f"bash {script_path}"],
                    # Konsole (KDE)
                    ["konsole", "-e", "bash", script_path],
                    # Terminal (macOS)
                    ["osascript", "-e", f'tell application "Terminal" to do script "bash {script_path}"']
                ]
                
                terminal_process = None
                for cmd_attempt in terminal_commands:
                    try:
                        terminal_process = subprocess.Popen(
                            cmd_attempt,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        self.logger.info(f"Launched {self.config.name} in terminal using {cmd_attempt[0]}")
                        break
                    except FileNotFoundError:
                        continue
                
                if terminal_process is None:
                    # Fallback: launch in background without terminal
                    self.logger.warning(f"No terminal emulator found, launching {self.config.name} in background")
                    terminal_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                
                # Store the terminal process (not the actual ROS node process)
                self.state.process = terminal_process
                self.state.pid = terminal_process.pid
                self.state.start_time = datetime.now()
                self.state.state = NodeState.RUNNING
                self.state.last_error = None
                
                return True
                
            finally:
                # Don't remove the script immediately, let the terminal process handle it
                pass
                
        except Exception as e:
            error_msg = f"Failed to start {self.config.name} in terminal: {str(e)}"
            self.logger.error(error_msg)
            self.state.state = NodeState.ERROR
            self.state.last_error = error_msg
            return False
        
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
            
            # Start the process based on use_terminal flag
            if self.config.use_terminal:
                success = self._start_in_terminal(cmd)
                if not success:
                    return False
            else:
                # Start the process normally
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
            
            # For terminal nodes, we're stopping the terminal process
            # The actual ROS node should stop when the terminal closes
            if self.config.use_terminal:
                self.logger.info(f"Closing terminal for node {self.config.name}")
            
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
        
        For terminal nodes, this checks if the terminal process is still active.
        If the terminal is closed, it automatically updates the node state.
        
        Returns:
            bool: True if the process exists and is running, False otherwise
        """
        if self.state.process is None:
            return False
        
        # Check if process is still running
        is_alive = self.state.process.poll() is None
        
        # If process died and this was a terminal node, update state
        if not is_alive and self.config.use_terminal and self.state.state == NodeState.RUNNING:
            self.logger.info(f"Terminal for node {self.config.name} was closed by user")
            self.state.state = NodeState.STOPPED
            self.state.pid = None
            self.state.last_error = None
        
        return is_alive
    
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
