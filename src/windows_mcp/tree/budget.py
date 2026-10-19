"""Bounds how many UI elements a single tree capture may collect.

Some applications expose enormous flat lists/grids through UI Automation
(e.g. an unfiltered inventory grid with thousands of rows). Walking and
serializing every row can stall the target application for minutes and can
produce a response too large for the calling client to handle. TreeElementBudget
gives Tree.get_state a cheap, dependency-free way to stop early once a
configurable element count is reached, while still returning a partial —
clearly marked as truncated — result instead of hanging or failing outright.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_MAX_TREE_ELEMENTS = 500


def resolve_max_tree_elements(env=None) -> int:
    """Read the tree-capture element limit from the environment."""
    source = os.environ if env is None else env
    raw = source.get("WINDOWS_MCP_MAX_TREE_ELEMENTS", "")
    if not raw.strip():
        return DEFAULT_MAX_TREE_ELEMENTS
    try:
        parsed = int(raw.strip())
    except ValueError:
        return DEFAULT_MAX_TREE_ELEMENTS
    if parsed < 1:
        return DEFAULT_MAX_TREE_ELEMENTS
    return parsed


class TreeElementBudget:
    """Tracks how many output-affecting elements a tree traversal has captured."""

    def __init__(self, limit: int = DEFAULT_MAX_TREE_ELEMENTS) -> None:
        self.limit = max(1, limit)
        self.count = 0
        self.truncated = False

    @property
    def exhausted(self) -> bool:
        return self.count >= self.limit

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.count)

    def try_consume(self, amount: int = 1) -> bool:
        """Register `amount` newly captured elements.

        Returns False (and marks the budget truncated) once the limit is
        reached; the caller should then stop appending/recursing further.
        """
        if amount <= 0:
            return not self.exhausted
        if self.exhausted:
            self.truncated = True
            return False
        if amount > self.remaining:
            self.count = self.limit
            self.truncated = True
            return False
        self.count += amount
        if self.exhausted:
            self.truncated = True
        return True
