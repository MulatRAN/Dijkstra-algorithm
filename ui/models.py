"""Small presentation models shared by the interface."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class TraceStep:
    """Presentation model for a single algorithm animation step."""

    node: Optional[str]
    distance: float
    visited: Tuple[str, ...]
    updated_nodes: Tuple[str, ...]
    explanation: str
