from __future__ import annotations

import random
from collections import deque

import numpy as np

from .base import Observation


class DQNController:
    """Adapter that preserves the existing DQN behavior.

    This keeps Torch imports and training logic out of Fighter.

    Note: Torch is imported lazily so match-mode / remote-mode can run
    without requiring torch on low-resource machines.
    """

    name = "dqn"

    def __init__(self, *, screen_width: int):
        # Lazy import torch to avoid heavy import cost when unused.
        import torch
        import torch.nn as nn
        import torch.optim as optim

        class DQN(nn.Module):
            def __init__(self, input_dim, output_dim):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(input_dim, 256),
                    nn.ReLU(),
                    nn.Linear(256, 256),
                    nn.ReLU(),
                    nn.Linear(256, 128),
                    nn.ReLU(),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, output_dim),
                )

            def forward(self, x):
                return self.layers(x)

        self._torch = torch
        self._optim = optim
        self._nn = nn

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.state_dim = 4
        self.action_space = 5
        self.gamma = 0.99
        self.batch_size = 64
        self.lr = 1e-4
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995
        self.memory = deque(maxlen=10000)
        self.train_start = 1000
        self.update_target_steps = 1000
        self.step_count = 0
        self.screen_width = screen_width

        self.policy_net = DQN(self.state_dim, self.action_space).to(self.device)
        self.target_net = DQN(self.state_dim, self.action_space).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)

        self._prev_state = None
        self._prev_action = None

    def _state_vec(self, obs: Observation) -> np.ndarray:
        dx = (obs.self_x - obs.opp_x) / obs.screen_width
        dy = (obs.self_y - obs.opp_y) / (obs.screen_width / 2)
        h1 = obs.self_health / 100.0
        h2 = obs.opp_health / 100.0
        return np.array([dx, dy, h1, h2], dtype=np.float32)

    def _select_action(self, state: np.ndarray) -> int:
        if random.random() < self.epsilon:
            return random.randrange(self.action_space)
        state_v = self._torch.tensor(state, device=self.device).unsqueeze(0)
        with self._torch.no_grad():
            qvals = self.policy_net(state_v)
        return int(qvals.argmax().cpu().numpy())

    def _remember(self, s, a, r, s2, done):
        self.memory.append((s, a, r, s2, done))

    def _optimize(self):
        if len(self.memory) < max(self.train_start, self.batch_size):
            return
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states_arr = np.array(states, dtype=np.float32)
        next_states_arr = np.array(next_states, dtype=np.float32)

        states_v = self._torch.from_numpy(states_arr).to(self.device)
        next_states_v = self._torch.from_numpy(next_states_arr).to(self.device)
        actions_v = self._torch.tensor(actions, dtype=self._torch.long, device=self.device).unsqueeze(1)
        rewards_v = self._torch.tensor(rewards, dtype=self._torch.float32, device=self.device).unsqueeze(1)
        dones_v = self._torch.tensor(dones, dtype=self._torch.float32, device=self.device).unsqueeze(1)

        q_pred = self.policy_net(states_v).gather(1, actions_v)
        with self._torch.no_grad():
            q_next = self.target_net(next_states_v).max(1)[0].unsqueeze(1)
            q_target = rewards_v + (1.0 - dones_v) * self.gamma * q_next

        loss = self._nn.MSELoss()(q_pred, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def act(self, obs: Observation) -> int:
        state = self._state_vec(obs)
        action = self._select_action(state)

        # Training signal is computed in Fighter.step_from_action, which returns reward/done.
        # Here we just return action. The env loop will call record() after stepping.
        self._prev_state = state
        self._prev_action = action
        return action

    def record(self, *, reward: float, next_obs: Observation, done: bool):
        if self._prev_state is None or self._prev_action is None:
            return
        next_state = self._state_vec(next_obs)
        self._remember(self._prev_state, self._prev_action, reward, next_state, done)
        self._optimize()

        self.step_count += 1
        if self.step_count % self.update_target_steps == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
