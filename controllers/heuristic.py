from __future__ import annotations

from .base import Observation


class HeuristicController:
    """A tiny baseline bot.

    Not smart, but useful to prove the control plumbing.
    """

    name = "heuristic"

    def act(self, obs: Observation) -> int:
        # If opponent is close, attack sometimes.
        dx = obs.opp_x - obs.self_x
        dist = abs(dx)

        # If in attack cooldown, reposition.
        if obs.self_attack_cooldown > 0:
            return 1 if dx < 0 else 2  # move toward opponent

        # Close enough: attack.
        if dist < 140:
            return 4  # heavy attack

        # Far: walk toward opponent.
        return 1 if dx < 0 else 2
