"""Thread-safe progress state of a running restraint analysis.

The pipeline runs inside a (blocking) Dash callback. The GUI polls
:func:`snapshot` from a separate request to show what is happening. Every
update is also printed to the terminal.
"""

import threading
import time
from typing import Dict, Optional

_LOCK = threading.Lock()
_STATE: Dict[str, object] = {
    "active": False, "fraction": 0.0, "message": "", "started": None, "error": None,
}


def start(message: str = "Starting restraint analysis") -> None:
    with _LOCK:
        _STATE.update(active=True, fraction=0.0, message=message,
                      started=time.time(), error=None)
    print(f"[restraint] {message}", flush=True)


def update(fraction: float, message: str) -> None:
    """Set overall progress (0..1) and the current step description."""
    with _LOCK:
        _STATE.update(fraction=max(0.0, min(1.0, fraction)), message=message)
    print(f"[restraint] {fraction * 100:5.1f} %  {message}", flush=True)


def finish(error: Optional[str] = None) -> None:
    with _LOCK:
        _STATE.update(active=False, fraction=1.0 if error is None else _STATE["fraction"],
                      error=error,
                      message="Failed" if error else "Done")
    print(f"[restraint] {'failed: ' + error if error else 'done'}", flush=True)


def snapshot() -> Dict[str, object]:
    with _LOCK:
        state = dict(_STATE)
    started = state.pop("started")
    state["elapsed"] = time.time() - started if started else 0.0
    return state
