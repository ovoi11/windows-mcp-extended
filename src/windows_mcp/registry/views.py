"""
Data models and constants for registry operations.
"""

from typing import Literal

ALLOWED_REGISTRY_TYPES = frozenset(
    {
        "String",
        "ExpandString",
        "Binary",
        "DWord",
        "MultiString",
        "QWord",
    }
)

RegistryType = Literal[
    "String",
    "ExpandString",
    "Binary",
    "DWord",
    "MultiString",
    "QWord",
]
