from __future__ import annotations

import random
from typing import Any


class RLAgent:
    """Simple placeholder RL agent policy."""

    def __init__(self, logger):
        self.logger = logger
        self.actions = ["forward", "left", "right", "hover"]

    def select_action(self, state: dict[str, Any]) -> str:
        _ = state
        action = random.choice(self.actions)
        self.logger.debug("RL agent selected action: %s", action)
        return action
