from __future__ import annotations

import asyncio
import json
import threading
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class RemoteState:
    last_action_p1: int = 0
    last_action_p2: int = 0


class BattleAgentsWSServer:
    """Authoritative WebSocket server run by the game loop.

    Controllers connect and send actions; spectators (future) can subscribe to state.

    Minimal protocol (v0):
      - server -> client: {"type":"obs","player":1|2, "obs":{...}}
      - client -> server: {"type":"action","player":1|2, "action":<int>}

    The game loop never blocks on network. If no action arrives, it uses last_action (default 0=noop).
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self._state = RemoteState()
        self._latest_obs: Dict[int, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._clients = set()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def set_obs(self, player: int, obs_json: Dict[str, Any]):
        with self._lock:
            self._latest_obs[player] = obs_json

    def get_action(self, player: int) -> int:
        with self._lock:
            return self._state.last_action_p1 if player == 1 else self._state.last_action_p2

    # ---------------- internal ----------------

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.create_task(self._serve())
        self._loop.create_task(self._broadcast_loop())
        self._loop.run_forever()

    async def _serve(self):
        import websockets  # pip install websockets

        async def handler(ws):
            self._clients.add(ws)
            try:
                async for msg in ws:
                    try:
                        data = json.loads(msg)
                    except Exception:
                        continue
                    if data.get("type") == "action":
                        p = int(data.get("player", 0) or 0)
                        a = int(data.get("action", 0) or 0)
                        if p in (1, 2):
                            with self._lock:
                                if p == 1:
                                    self._state.last_action_p1 = a
                                else:
                                    self._state.last_action_p2 = a
            finally:
                self._clients.discard(ws)

        await websockets.serve(handler, self.host, self.port)

    async def _broadcast_loop(self):
        # Broadcast latest observations at ~30Hz (decoupled from render FPS).
        while True:
            await asyncio.sleep(1 / 30)
            if not self._clients:
                continue
            with self._lock:
                payloads = {
                    p: {"type": "obs", "player": p, "obs": obs}
                    for p, obs in self._latest_obs.items()
                }
            if not payloads:
                continue
            dead = []
            for ws in list(self._clients):
                try:
                    # send both players' obs (clients can filter by player)
                    for p in (1, 2):
                        if p in payloads:
                            await ws.send(json.dumps(payloads[p]))
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self._clients.discard(ws)
