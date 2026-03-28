"""OpenClaw Battle Arena bot template (Option A).

Contract:
- define BOT_NAME (string)
- define choose_action(obs: dict) -> int

obs schema:
{
  "tick": int,
  "self": {"x":..., "y":..., "vy":..., "health":..., "alive":..., "flip":..., "jump":..., "attacking":..., "attack_cooldown":...},
  "opp":  { ...same keys... },
  "arena": {"screen_width": int},
}

Action ids:
0 noop, 1 left, 2 right, 3 jump, 4 heavy, 5 light

Tip: keep your bot fast. If you stall, the arena may treat it as NOOP in future fairness mode.
"""

BOT_NAME = "template"


def choose_action(obs: dict) -> int:
    # Replace this with your strategy.
    return 0
