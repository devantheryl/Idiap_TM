# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 11:51:35 2022

@author: LDE
"""
import json
import os
from collections import deque
import wandb
import numpy as np
from tensorforce import Environment, Runner, Agent
from src.Production_line2 import Production_line
import src.utils as utils

class TF_environment(Environment):
    
    def __init__(self):
        
        super().__init__()
        self.production_line = Production_line()
        self.max_step_per_episode = 100
        
        
    def states(self):
        
        return dict(type="float", shape=(self.production_line.state_size))
    
    def actions(self):
        return dict(type="int", num_values = len(self.production_line.actions_space))
    
    def max_episode_timesteps(self):
        return self.max_step_per_episode
    
    def close(self):
        super().close()
        
    def reset(self):
        # Initial state and associated action mask
        self.production_line = Production_line()
        action_mask = self.production_line.get_mask()
        
        # Add action mask to states dictionary (mask item is "[NAME]_mask", here "action_mask")
        states = dict(state = self.production_line.get_state(),  action_mask = action_mask)
        
        return states
    
    def execute(self,actions):
        # Compute terminal and reward
        
        next_state,reward, done  = self.production_line.step(actions)

        action_mask =self.production_line.get_mask()

        # Add action mask to states dictionary (mask item is "[NAME]_mask", here "action_mask")
        states = dict(state=next_state, action_mask=action_mask)

        return states, done, reward
    
    def get_env(self):
        return self.production_line
    
    
if __name__ == '__main__':
    
    with open("src/config.json") as json_file:
        config = json.load(json_file)
    wandb_activate = True
    if wandb_activate:
        run = wandb.init(
          project="auto_scheduler_3jobs_TensorForce",
          entity="devantheryl",
          notes="tuning hyperparamters",
          config=config,
        )
    os.makedirs("model/" + run.project, exist_ok=True)
    os.makedirs("model/" + run.project + "/" + run.name, exist_ok=True)
    print(run.name)
    print(run.project)
    
    score_mean = deque(maxlen = 100)
    score_min = -10000
    
    params_agent = config["params_agent"]
    environment = Environment.create(environment=TF_environment)
    
    num_episode = params_agent["n_episode"]
    
    agent = Agent.create(
        agent='ddqn',
        states = environment.states(),
        actions = environment.actions(),
        memory=params_agent["memory"],
        batch_size = params_agent["batch_size"],
        network = [
            dict(type = 'dense', size = params_agent["nbr_neurone_first_layer"], activation = params_agent["activation_first_layer"]),
            dict(type = 'dense', size = params_agent["nbr_neurone_second_layer"], activation = params_agent["activation_second_layer"]),
            #dict(type = 'dense', size = len(environment.get_env().actions_space), activation = 'tanh')
            ],
        update_frequency = params_agent["UPDATE_FREQ"], 
        learning_rate = params_agent["learning_rate"],
        horizon = 1,
        target_sync_frequency  = params_agent["NETW_UPDATE_FREQ"],
        exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*0.9), initial_value = params_agent["epsilon"], final_value = params_agent["epsilon_min"]),
        config = dict(seed = 0),
        tracking = 'all'
    )
    
    print(agent.get_architecture())
    step = 0
    for i in range(num_episode):

        # Initialize episode
        states = environment.reset()
        terminal = False
        reward_tot = 0
        while not terminal:
            # Episode timestep
            actions = agent.act(states=states)
            states, terminal, reward = environment.execute(actions=actions)
            agent.observe(terminal=terminal, reward=reward)
            reward_tot += reward
            tracked = agent.tracked_tensors()
            if wandb_activate:
                wandb.log(
                    {
                        "baseline-loss" : tracked["agent/baseline-loss"],
                        "baseline-objective-loss" : tracked["agent/baseline-objective-loss"],
                        "baseline-regularization-loss" : tracked["agent/baseline-regularization-loss"],
                        "entropy" : tracked["agent/entropy"],
                        "exploration" : tracked["agent/exploration/exploration"],
                        "kl-divergence" : tracked["agent/kl-divergence"],
                        "policy-loss" : tracked["agent/policy-loss"],
                        "policy-objective-loss" : tracked["agent/policy-objective-loss"],
                        "policy-regularization-loss" : tracked["agent/policy-regularization-loss"],
                        "update-return" : tracked["agent/update-return"],
                        
                    },
                    step =step
                )
            step+=1
            
        score_mean.append(reward_tot)
        if score_min < reward_tot:
                score_min = reward_tot
        print("episode: ", i, "  reward : ",reward_tot, "mean_reward : ", np.mean(score_mean), "score min : ", score_min)
        if wandb_activate:
            wandb.log(
                {
                    "reward" : reward_tot,
                }
            )
        
    states = environment.reset()
    terminal = False
    reward_tot = 0

    while not terminal:
        # Episode timestep
        actions = agent.act(states=states, independent=True)
        states, terminal, reward = environment.execute(actions=actions)
        
        reward_tot += reward
        
    print("final result : ", reward_tot)
    if wandb_activate:
            wandb.run.summary["score_minimum"] = score_min
            wandb.run.summary['evaluation return:'] = reward_tot
    
tracked = agent.tracked_tensors()
planning = environment.get_env().get_gant_formated()
utils.visualize(planning)
agent.close()
environment.close()