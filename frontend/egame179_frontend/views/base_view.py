from dataclasses import dataclass
from typing import Callable


@dataclass
class View:
    name: str
    icon: str
    view: Callable
