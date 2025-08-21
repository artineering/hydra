```
██╗  ██╗██╗   ██╗██████╗ ██████╗  █████╗ 
██║  ██║╚██╗ ██╔╝██╔══██╗██╔══██╗██╔══██╗
███████║ ╚████╔╝ ██║  ██║██████╔╝███████║
██╔══██║  ╚██╔╝  ██║  ██║██╔══██╗██╔══██║
██║  ██║   ██║   ██████╔╝██║  ██║██║  ██║
╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
```

# Hydra - Hybrid Dynamic Robot Agent

Hydra is a Python-based node management system for ROS2 that provides centralized configuration, lifecycle management, and monitoring of distributed robotics nodes. It enables declarative node deployment through YAML configuration files with support for both background and interactive terminal-based execution.

## Features

- **Configuration-driven deployment** - Define all nodes in a single YAML file
- **Lifecycle management** - Start, stop, and monitor node processes
- **Terminal integration** - Launch interactive nodes in separate terminal windows
- **Process monitoring** - Track node status, PIDs, and automatic restart capabilities
- **ROS2 integration** - Full support for namespaces, parameter passing, and topic remapping
- **Graceful shutdown** - Proper signal handling and cleanup

## Project Structure

```
src/hydra/
|-- core/
      |-- managed/
            |-- internal/        # Configuration and state management
                  |-- nodeConfig.py    # Node configuration data class
                  |-- nodeState.py     # Node lifecycle states
                  |-- nodeRuntimeState.py # Runtime state tracking
            |-- node.py          # Main ManagedNode class
            |-- service.py       # Service layer (future)
      |-- utils/
            |-- config_parser.py # YAML configuration parser
      |-- agent/               # Agent system (future)
      |-- webserver/           # Web interface (future)
|-- config/
      |-- configuration.yaml  # Example TurtleSim configuration
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd hydra

# Install dependencies
pip install pyyaml

# Install in development mode
pip install -e .
```

### 2. Configuration

Create or modify `src/hydra/config/configuration.yaml`:

```yaml
nodes:
  - name: "my_node"
    package: "my_package"
    executable: "my_executable"
    namespace: "/my_namespace"
    enabled: true
    use_terminal: false
    parameters:
      param1: value1
    remappings:
      old_topic: new_topic
```

### 3. Running Nodes

```bash
# Run the test script
python3 tests/test_run_nodes.py
```

## Configuration Reference

### Node Configuration

Each node in the configuration supports the following fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | *required* | Unique identifier for the node |
| `package` | string | *required* | ROS2 package name |
| `executable` | string | *required* | Executable name within the package |
| `namespace` | string | "/" | ROS2 namespace |
| `enabled` | boolean | true | Whether to start the node |
| `use_terminal` | boolean | false | Launch in separate terminal window |
| `auto_restart` | boolean | true | Automatically restart on failure |
| `respawn_delay` | float | 2.0 | Seconds to wait before restart |
| `parameters` | dict | {} | ROS2 parameters to set |
| `remappings` | dict | {} | Topic/service name remappings |

### System Configuration

Global system settings can be configured under the `system` key:

```yaml
system:
  log_level: "INFO"
  max_restart_attempts: 5
  health_check_interval: 10.0
  graceful_shutdown_timeout: 15.0
```

## Usage Examples

### Basic Node Management

```python
from hydra.core.utils.config_parser import ConfigurationParser
from hydra.core.managed.node import ManagedNode

# Parse configuration
parser = ConfigurationParser()
configs = parser.parse_file("config/configuration.yaml")

# Create and start nodes
for config in configs:
    node = ManagedNode(config)
    if config.enabled:
        node.start()
```

### Interactive Terminal Nodes

For nodes requiring user interaction (like teleoperation):

```yaml
- name: "turtle_teleop"
  package: "turtlesim"
  executable: "turtle_teleop_key"
  use_terminal: true  # Opens in separate terminal
  enabled: true
```

### TurtleSim Demo

The included configuration demonstrates a complete TurtleSim setup:

```bash
# Run the TurtleSim demo
python3 tests/test_run_nodes.py
```

This will launch:
- TurtleSim simulator window
- Keyboard teleop control in a separate terminal
- Additional turtle nodes with different configurations

## Architecture

### Core Components

- **ManagedNode**: Central class managing individual ROS2 node processes
- **NodeConfig**: Data class defining node configuration and parameters
- **NodeState**: Enum tracking lifecycle states (UNINITIALIZED, RUNNING, STOPPED, ERROR)
- **ConfigurationParser**: YAML parser converting config files to NodeConfig objects

### Process Management

- **Background nodes**: Run with stdout/stderr capture for logging
- **Terminal nodes**: Launch in separate terminal windows with user interaction
- **Signal handling**: Proper cleanup when terminals are closed
- **Graceful shutdown**: SIGTERM followed by SIGKILL if necessary

### State Management

Node states are tracked through the lifecycle:
1. `UNINITIALIZED` - Node created but not configured
2. `INITIALIZED` - Configuration loaded and validated
3. `RUNNING` - Process active and monitored
4. `STOPPED` - Gracefully terminated
5. `ERROR` - Failed to start or crashed

## Development

### Building

```bash
# Using Poetry
poetry build

# Using pip
pip install build
python -m build
```

### Testing

```bash
# Run configuration parser test
python3 tests/test_config_parser.py

# Run node management test
python3 tests/test_run_nodes.py
```

### Dependencies

- Python >= 3.12
- PyYAML >= 6.0.2
- ROS2 (for node execution)

## Roadmap

- [ ] Web-based management interface
- [ ] Distributed agent system
- [ ] Health monitoring and alerting
- [ ] Configuration validation and schema
- [ ] Docker/container support
- [ ] Service discovery and registration

## License

This project is licensed under the Apache License 2.0

```
Copyright 2025 Hydra Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Citing

If you use this software in your research, please cite:
```
@software{hydra,
  title={Hydra - ROS2-based Managed Node Agent},
  author={Siddharth Vaghela},
  year={2025},
  url={https://github.com/artineering/hydra}
}
```

