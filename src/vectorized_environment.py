# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 11:46:29 2022

@author: LDE
"""

# Copyright 2021 Tensorforce Team. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import numpy as np
import os
from tensorforce import Environment, Runner, Agent
import time

class VectorizedEnvironment(Environment):
    """
    Example vectorized environment, illustrating best-practice implementation pattern.
    State space: position in [0, 10].
    Action space: movement in {-1, 0, 1}.
    Random start in [0, 3] or [7, 10].
    Positive reward for moving towards the center 5.
    """

    def __init__(self):
        super().__init__()
        self.i = 0

    def states(self):
        return dict(type='int', num_values=11)

    def actions(self):
        return dict(type='int', num_values=3)

    def is_vectorizable(self):
        return True  # Indicates that environment is vectorizable

    def reset(self, num_parallel=None):
        
        self.i += 1
        #print(self.i)
        # Always for vectorized environments: initialize parallel indices
        self._is_parallel = (num_parallel is not None)
        if self._is_parallel:
            self._parallel_indices = np.arange(num_parallel)
        else:
            self._parallel_indices = np.arange(1)

        # Vectorized environment logic
        is_high = (np.random.random_sample(size=self._parallel_indices.shape) < 0.5)
        offset = np.random.randint(4, size=self._parallel_indices.shape)
        self._states = np.where(is_high, 10 - offset, offset)

        # Always for vectorized environments: return un-/vectorized values
        if self._is_parallel:
            return self._parallel_indices.copy(), self._states.copy()
        else:
            return self._states[0]

    def execute(self, actions):
        # Always for vectorized environments: expand actions if non-vectorized
        if not self._is_parallel:
            actions = np.expand_dims(actions, axis=0)

        # Vectorized environment logic
        reward = np.select(
            condlist=[self._states < 5, self._states > 5],
            choicelist=[(actions == 2).astype(np.float32), (actions == 0).astype(np.float32)],
            default=np.ones(shape=self._parallel_indices.shape, dtype=np.float32)
        )
        terminal = (np.random.random_sample(size=self._parallel_indices.shape) < 0.1)
        self._states = np.clip(self._states + (actions - 1), a_min=0, a_max=10)

        # Always for vectorized environments: update parallel indices and states,
        #                                     and return un-/vectorized values
        if self._is_parallel:
            self._parallel_indices = self._parallel_indices[~terminal]
            self._states = self._states[~terminal]
            return self._parallel_indices.copy(), self._states.copy(), terminal, reward
        else:
            return self._states[0], terminal.item(), reward.item()


def main():
    
    print(os.getcwd())
    environment = VectorizedEnvironment()
    agent = Agent.create(
        agent="ddqn",
        states = environment.states(),
        actions = environment.actions(),
        #max_episode_timesteps = 10,
        memory=100000,
        batch_size = 32,
        network = "auto",
        update_frequency = 2,
        learning_rate = 0.001,
        #huber_loss = huber_loss,
        horizon = 10,
        discount = 0.99,
        target_update_weight = 1.0 ,
        target_sync_frequency  = 50,
        exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(1000*0.9), initial_value = 0.5, final_value = 0.01),
        config = dict(seed = 1),
        tracking = 'all',
        parallel_interactions  = 1,
        )
        # Non-vectorized runner
    start = time.time()
    for i in range(1,100+1):

        # Initialize episode
        states = environment.reset()
        terminal = False
        reward_tot = 0
        step = 0
        while not terminal:
            # Episode timestep

            actions = agent.act(states=states, independent = False)
            
            
            states, terminal, reward = environment.execute(actions=actions)
            
            agent.observe(terminal=terminal, reward=reward)
            reward_tot += reward
            step+=1
        #print("episode : ", i, " reward : ", reward_tot)
            
    end = time.time()
    print(end - start)

    # Vectorized runner, automatically if num_parallel > 1 and environment.is_vectorizable()
    # (and remote argument not specified)
    
    start = time.time()
    runner = Runner(
        agent='scenario_test.json',
        environment=VectorizedEnvironment,
        max_episode_timesteps=10,
        num_parallel=16
    )
    runner.run(num_episodes=100)
    end = time.time()
    print(end - start)


if __name__ == '__main__':
    main()