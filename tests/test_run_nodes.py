#!/usr/bin/env python3
"""
Test script to create ManagedNodes from configuration and run them.
"""

import sys
import os
import time
import signal
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hydra.core.utils.config_parser import ConfigurationParser
from hydra.core.managed.node import ManagedNode

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NodeRunner:
    """Simple runner for managing multiple nodes."""
    
    def __init__(self):
        self.managed_nodes = []
        self.running = False
    
    def load_nodes_from_config(self, config_path: str):
        """Load all node configurations and create ManagedNode instances."""
        parser = ConfigurationParser()
        
        try:
            node_configs = parser.parse_file(config_path)
            logger.info(f"Loaded {len(node_configs)} node configurations from file")
            
            for config in node_configs:
                managed_node = ManagedNode(config)
                self.managed_nodes.append(managed_node)
                logger.info(f"Created ManagedNode: {config.name}")
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def start_enabled_nodes(self):
        """Start all enabled nodes."""
        logger.info("Starting enabled nodes...")
        
        for node in self.managed_nodes:
            if not node.config.enabled:
                logger.info(f"Skipping disabled node: {node.config.name}")
                continue
                
            try:
                success = node.start()
                if success:
                    logger.info(f"Started node: {node.config.name} (PID: {node.state.pid})")
                else:
                    logger.error(f"Failed to start node: {node.config.name}")
            except Exception as e:
                logger.error(f"Error starting {node.config.name}: {e}")
        
        self.running = True
    
    def stop_all_nodes(self):
        """Stop all running nodes."""
        logger.info("Stopping all nodes...")
        
        for node in self.managed_nodes:
            if node.is_running():
                try:
                    success = node.stop()
                    if success:
                        logger.info(f"Stopped node: {node.config.name}")
                    else:
                        logger.error(f"Failed to stop node: {node.config.name}")
                except Exception as e:
                    logger.error(f"Error stopping {node.config.name}: {e}")
        
        self.running = False
    
    def print_status(self):
        """Print status of all managed nodes."""
        print("\n" + "="*60)
        print("NODE STATUS")
        print("="*60)
        
        for node in self.managed_nodes:
            status = node.get_status()
            print(f"Name: {status['name']}")
            print(f"  Package: {node.config.package}")
            print(f"  Executable: {node.config.executable}")
            print(f"  Namespace: {node.config.namespace}")
            print(f"  State: {status['state']}")
            print(f"  Enabled: {status['enabled']}")
            print(f"  Running: {status['running']}")
            print(f"  PID: {status['pid']}")
            print(f"  Auto-restart: {node.config.auto_restart}")
            print(f"  Use terminal: {node.config.use_terminal}")
            if status['last_error']:
                print(f"  Last Error: {status['last_error']}")
            print("-" * 40)

# Global variable for signal handler
node_runner = None

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\nReceived interrupt signal, stopping nodes...")
    if node_runner:
        node_runner.stop_all_nodes()
    sys.exit(0)

def main():
    global node_runner
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    node_runner = NodeRunner()
    
    # Configuration file path
    config_path = os.path.join(os.path.dirname(__file__), "..", "src", "hydra", "config", "configuration.yaml")
    
    try:
        # Load nodes from configuration
        print("Loading nodes from configuration...")
        node_runner.load_nodes_from_config(config_path)
        
        # Show loaded nodes
        print(f"\nLoaded {len(node_runner.managed_nodes)} nodes from configuration")
        node_runner.print_status()
        
        # Ask user if they want to start the nodes
        response = input("\nDo you want to start the enabled nodes? (y/n): ").strip().lower()
        
        if response == 'y' or response == 'yes':
            node_runner.start_enabled_nodes()
            
            print("\nEnabled nodes are now running!")
            print("- Check the status below to see which nodes started successfully")
            print("- Nodes with use_terminal=true should run in separate terminals")
            print("- Press Ctrl+C to stop all nodes")
            print("\nStatus will be displayed every 10 seconds...\n")
            
            # Keep running and show periodic status
            try:
                while node_runner.running:
                    time.sleep(10)
                    node_runner.print_status()
                    
            except KeyboardInterrupt:
                pass
        else:
            print("Exiting without starting nodes.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    finally:
        if node_runner:
            node_runner.stop_all_nodes()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())