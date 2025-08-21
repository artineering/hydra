import subprocess

from .nodeState import NodeState
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class NodeRuntimeState:
    name: str
    state: NodeState = NodeState.UNINITIALIZED
    process: Optional[subprocess.Popen] = None
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    restart_count: int = 0
    last_error: Optional[str] = None