from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class IterationStep:
    step_number: int
    numericals: Dict[str, float]

    description: str

    plot_data: List[Dict[str, Any]] = field(default_factory=list)
