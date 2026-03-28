from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Optional

from .base import Observation


@dataclass
class ScriptSpec:
    path: str


def _load_module_from_path(path: str) -> ModuleType:
    path = os.path.abspath(path)
    name = f"battle_bot_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load bot script: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


class ScriptFileController:
    """Controller that calls a user-provided Python script.

    The script must define:
      - choose_action(obs) -> int

    Where obs is a JSON-serializable dict (see Observation.to_json()).
    """

    def __init__(self, *, script_path: str):
        self._script_path = script_path
        self._mod = _load_module_from_path(script_path)
        fn = getattr(self._mod, "choose_action", None)
        if not callable(fn):
            raise ValueError(f"Bot script {script_path} must define choose_action(obs) -> int")
        self._choose: Callable[[dict[str, Any]], int] = fn  # type: ignore[assignment]
        self.name = getattr(self._mod, "BOT_NAME", os.path.basename(script_path))

    def act(self, obs: Observation) -> int:
        # Pass dict to keep the script interface stable and language-agnostic.
        a = self._choose(obs.to_json())
        return int(a)
