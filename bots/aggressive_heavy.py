"""A simple aggressive bot: closes distance and heavy-attacks.

Uses jump occasionally to avoid getting stuck.
"""

BOT_NAME = "aggressive-heavy"


def choose_action(obs: dict) -> int:
    s = obs.get("self", {})
    o = obs.get("opp", {})
    sx = float(s.get("x", 0.0))
    ox = float(o.get("x", 0.0))
    dx = ox - sx
    dist = abs(dx)

    cooldown = int(s.get("attack_cooldown", 0) or 0)
    in_jump = bool(s.get("jump", False))

    # If close and not cooling down: heavy.
    if dist < 150 and cooldown == 0:
        return 4

    # If far, move toward.
    if dist >= 150:
        return 1 if dx < 0 else 2

    # If mid-range and not currently jumping, jump sometimes (simple deterministic toggle).
    if not in_jump and (obs.get("tick", 0) % 40 == 0):
        return 3

    return 1 if dx < 0 else 2
