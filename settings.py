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
# Options: "remote" (ws), "heuristic", "dqn", "script"
P1_CONTROLLER = "remote"    # warrior
P2_CONTROLLER = "heuristic" # wizard

# Option A (script bots): set controller to "script" and provide a script path.
P1_SCRIPT_PATH = "bots/aggressive_heavy.py"
P2_SCRIPT_PATH = "bots/aggressive_heavy.py"

# WebSocket server (used when any controller is "remote")
WS_HOST = "127.0.0.1"
WS_PORT = 8765
