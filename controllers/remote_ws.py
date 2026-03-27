from __future__ import annotations

from .base import Observation
from .ws_server import BattleAgentsWSServer


class RemoteWSController:
    """Controller backed by the game's internal WebSocket server.

    The game remains authoritative: it renders audio/visual and runs the physics.
    Remote clients only suggest actions.
    """

    def __init__(self, *, server: BattleAgentsWSServer, player: int):
        self.name = f"remote-ws-p{player}"
        self._server = server
        self._player = player

    def act(self, obs: Observation) -> int:
        # Push obs to server for broadcasting; use last received action.
        self._server.set_obs(self._player, obs.to_json())
        return int(self._server.get_action(self._player))
