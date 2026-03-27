"""Controllers for Battle-Agents.

A Controller chooses an action given an observation.

Design goals:
- Keep rendering/audio unchanged (Pygame loop stays authoritative).
- Support local (heuristic) and remote (WebSocket) controllers.
- Preserve existing behavior via a DQNController adapter.
"""
