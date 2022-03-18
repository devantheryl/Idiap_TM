# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 16:32:04 2022

@author: LDE
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 11:46:42 2022

@author: LDE
"""

import numpy as np
import pandas as pd
import sys
import os
import time
import argparse
import json
from collections import deque
import wandb

from src.TF_env_para import TF_environment
from tensorforce import Environment, Runner, Agent

import src.utils as utils
os.environ["WANDB_AGENT_MAX_INITIAL_FAILURES"]= "30"

REQUIRED_PYTHON = "3.8.5"



    

    
with open("src/config.json") as json_file:
        configs = json.load(json_file)

test_every = configs["test_every"]



num_episode = configs["n_episode"]
memory = configs["memory"]
batch_size = configs["batch_size"]
network = configs["network"]
update_frequency = configs["UPDATE_FREQ"]
learning_rate = configs["learning_rate"]
huber_loss = configs["huber_loss"]
horizon = configs["horizon"]
discount = configs["discount"]
target_update_weight  = configs["target_update_weight"]
target_sync_frequency  = configs["NETW_UPDATE_FREQ"]
epsilon = configs["epsilon"]
epsilon_min = configs["epsilon_min"]

score_mean = deque(maxlen = 300)
score_min = -10000


environment = Environment.create(environment=TF_environment)
step = 0
num_parallel = 4

agent = Agent.create(
    agent='ddqn',
    states = environment.states(),
    actions = environment.actions(),
    max_episode_timesteps = environment.max_episode_timesteps(),
    memory=memory,
    batch_size = batch_size,
    network = network,
    update_frequency = update_frequency,
    learning_rate = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*0.5), initial_value = 0.01, final_value = learning_rate),
    #huber_loss = huber_loss,
    horizon = horizon,
    discount = discount,
    target_update_weight = target_update_weight ,
    target_sync_frequency  = target_sync_frequency,
    exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*0.8), initial_value = epsilon, final_value = epsilon_min),
    config = dict(seed = 1),
    tracking = 'all',
    parallel_interactions  = num_parallel,
)

print(agent.get_architecture())

for i in range(0,num_episode,num_parallel):

    # Initialize episode
    parallel, states = environment.reset(num_parallel = num_parallel)
    terminal =  (parallel < 0)
    reward_tot = 0
    num_updates = 0
    while not terminal.all():
        # Episode timestep

        actions = agent.act(states=states, independent = False, parallel=parallel)
        
        next_parallel, states, terminal, reward = environment.execute(actions=actions)
        
        num_updates += agent.observe(terminal=terminal, reward=reward, parallel=parallel)
        reward_tot += reward.sum()
        tracked = agent.tracked_tensors()
        
        step+=1
    print('Episode {}: return={} updates={}'.format(
            i, reward_tot / num_parallel, num_updates
        ))
        
        #memoire.append(np.hstack((old_state,actions,reward,terminal)))
    
    
    
        
# Evaluate for 100 episodes
num_parallel = 4
num_episodes = 100
sum_rewards = 0.0
for _ in range(0, num_episodes, num_parallel):
    parallel, states = environment.reset(num_parallel=num_parallel)
    internals = agent.initial_internals()
    internals = [internals for _ in range(num_parallel)]
    terminal = (parallel < 0)  # all false
    while not terminal.all():
        actions, internals = agent.act(
            states=states, internals=internals, independent=True, deterministic=True
        )
        _, states, terminal, reward = environment.execute(actions=actions)
        internals = [internal for internal, term in zip(internals, terminal) if not term]
        sum_rewards += reward.sum()
print('Mean evaluation return:', sum_rewards / num_episodes)

# Close agent and environment
agent.close()
environment.close()
    


        