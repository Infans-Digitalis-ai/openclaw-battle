"""Battle-Agents runtime settings.

Keep defaults matching current visual/audio behavior.

Controllers:
- "dqn" (original training)
- "heuristic" (lightweight baseline)
- "remote" (WebSocket; external agent supplies actions)

Modes:
- TRAIN: endless episodes (original behavior)
- MATCH: best-of-N rounds (for spectator/competitive play)
"""

# MODE can be: "TRAIN" or "MATCH"
MODE = "MATCH"

# Round format when MODE="MATCH"
MATCH_BEST_OF = 3  # best-of-3 rounds

# Controller selection
P1_CONTROLLER = "remote"    # warrior
P2_CONTROLLER = "heuristic" # wizard (start with heuristic so we can watch P1 remote work)

# WebSocket server (used when any controller is "remote")
WS_HOST = "127.0.0.1"
WS_PORT = 8765
