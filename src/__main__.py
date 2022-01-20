t# -*- coding: utf-8 -*-
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

from src.TF_env import TF_environment
from tensorforce import Environment, Runner, Agent

import src.utils as utils


REQUIRED_PYTHON = "3.8.5"

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description = 'Program options')
    parser.add_argument('-train', dest = 'train', action = 'store_true', help = 'Train the model given the paramters in config.json')
    parser.add_argument('-wandb', dest = 'wandb_activate', action = 'store_true' , help = 'Use the wandb framework to save the hyperparameters')
    
    
    
    args = parser.parse_args()
    
    start = time.time()
    
    print("Begin of the training phase")
    
    if args.train:
        with open("src/config.json") as json_file:
            config = json.load(json_file)
        
        if args.wandb_activate:
            run = wandb.init(
              project="auto_scheduler_4jobs_TensorForce",
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
                step+=1
            if args.wandb_activate:
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
                
            score_mean.append(reward_tot)
            if score_min < reward_tot:
                    score_min = reward_tot
            print("episode: ", i, "  reward : ",reward_tot, "mean_reward : ", np.mean(score_mean), "score min : ", score_min)
            if args.wandb_activate:
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
        if args.wandb_activate:
                wandb.run.summary["score_minimum"] = score_min
                wandb.run.summary['evaluation return:'] = reward_tot
        
        tracked = agent.tracked_tensors()
        planning = environment.get_env().get_gant_formated()
        utils.visualize(planning)
        agent.close()
        environment.close()