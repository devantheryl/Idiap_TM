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

from src.TF_env import TF_environment
from tensorforce import Environment, Runner, Agent

import src.utils as utils


REQUIRED_PYTHON = "3.8.5"

def train_model(wandb_activate = True,sweep = True):
    with open("src/config.json") as json_file:
            configs = json.load(json_file)
        
    if wandb_activate:
        if sweep:
            run = wandb.init(config = configs)    
        else:
            run = wandb.init(

              project="auto_scheduler_1jobs_TensorForce",

              entity="devantheryl",
              notes="tuning hyperparamters",
              config=configs,
            )
        config = wandb.config
        
        os.makedirs("model/" + run.project, exist_ok=True)
        os.makedirs("model/" + run.project + "/" + run.name, exist_ok=True)
        print(run.name)
        print(run.project)
        
        num_episode = config.n_episode
        memory = config.memory
        batch_size = config.batch_size
        nbr_neurone_first_layer = config.nbr_neurone_first_layer
        activation_first_layer = config.activation_first_layer
        nbr_neurone_second_layer = config.nbr_neurone_second_layer
        activation_second_layer = config.activation_second_layer
        update_frequency = config.UPDATE_FREQ
        learning_rate = config.learning_rate
        huber_loss = config.huber_loss
        horizon = config.horizon
        discount = config.discount
        target_sync_frequency  = config.NETW_UPDATE_FREQ
        epsilon = config.epsilon
        epsilon_min = config.epsilon_min
        
    else:
        num_episode = configs["n_episode"]
        memory = configs["memory"]
        batch_size = configs["batch_size"]
        nbr_neurone_first_layer = configs["nbr_neurone_first_layer"]
        activation_first_layer = configs["activation_first_layer"]
        nbr_neurone_second_layer = configs["nbr_neurone_second_layer"]
        activation_second_layer = configs["activation_second_layer"]
        update_frequency = configs["UPDATE_FREQ"]
        learning_rate = configs["learning_rate"]
        huber_loss = configs["huber_loss"]
        horizon = configs["horizon"]
        discount = configs["discount"]
        target_sync_frequency  = configs["NETW_UPDATE_FREQ"]
        epsilon = configs["epsilon"]
        epsilon_min = configs["epsilon_min"]
    
    score_mean = deque(maxlen = 100)
    score_min = -10000
    
    
    environment = Environment.create(environment=TF_environment)
    
    agent = Agent.create(
        agent='ddqn',
        states = environment.states(),
        actions = environment.actions(),
        memory=memory,
        batch_size = batch_size,
        network = [
            dict(type = 'dense', size = nbr_neurone_first_layer, activation = activation_first_layer),
            dict(type = 'dense', size = nbr_neurone_second_layer, activation = activation_second_layer),
            ],
        update_frequency = update_frequency,
        learning_rate = learning_rate,
        huber_loss = huber_loss,
        horizon = horizon,
        discount = discount,
        target_sync_frequency  = target_sync_frequency,
        exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*0.9), initial_value = epsilon, final_value = epsilon_min),
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
        if wandb_activate:
            wandb.log(
                {
                    "exploration" : tracked["agent/exploration/exploration"],
                    "policy-loss" : tracked["agent/policy-loss"],
                    "policy-objective-loss" : tracked["agent/policy-objective-loss"],
                    "update-return" : tracked["agent/update-return"],
                    
                },
                step =step
            )
            
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
        if i %100 == 0:
            planning = environment.get_env().get_gant_formated()

            path_img = "model/" + run.project + "/" +  run.name +"/" + '{:010d}'.format(i) + ".png"
            utils.visualize(planning,path_img)
            agent.save("model/" + run.project + "/" +  run.name +"/", '{:010d}'.format(i), format = "hdf5")

            #path_img = "model/" + run.project + "/" +  run.name +"/" + '{:010d}'.format(i) + ".png"
            try: 
                utils.visualize(planning)
            except:
                print("impossible to viusalize")
            #agent.save("model/" + run.project + "/" +  run.name +"/", '{:010d}'.format(i), format = "hdf5")
        
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
        wandb.log(
            {
                "score_minimum" : score_min,
                "evaluation_return" : reward_tot     
            }
        )
        run.finish()
    
    tracked = agent.tracked_tensors()
    planning = environment.get_env().get_gant_formated()
    try :
        utils.visualize(planning)
    except:
        print("impossible to viusalize")
    agent.close()
    environment.close()
    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description = 'Program options')
    parser.add_argument('-train', dest = 'train', action = 'store_true', help = 'Train the model given the paramters in config.json')
    parser.add_argument('-wandb', dest = 'wandb_activate', action = 'store_true' , help = 'Use the wandb framework to save the hyperparameters')
    parser.add_argument('-sweep', dest = 'sweep', action = 'store_true' , help = 'Launch a bayesian hyperparameters search process over the range of parameters in config.json')
    
    
    args = parser.parse_args()
    
    start = time.time()
    
    print("Begin of the training phase")
    
    if args.train:
        print("train model")
        train_model(args.wandb_activate,False)
        
    if args.sweep:
        print("sweep model")
        sweep_configs = {
            "name" : "my_sweep",
            "project" : "sweep_4_job",
            "entity" : "devantheryl",
            "method": "bayes",
            "metric": {
                "name": "evaluation_return",
                "goal": "maximize",
            },
            "parameters": {
                "batch_size": {
                    "values": [128,256,512]
                },
                "n_episode": {
                    "values": [4000,8000]
                },
                "UPDATE_FREQ": {
                    "values": [2,4,8,16]
                },
                "NETW_UPDATE_FREQ": {
                    "values": [10,50]
                },
                "epsilon": {
                    "values": [1,0.5]
                },
                "epsilon_min": {
                    "values": [0.05]
                },
                "learning_rate": {
                    "values": [0.0005]
                },
                "huber_loss": {
                    "values": [0.9]
                },
                "horizon": {
                    "values": [1,4,10]
                },
                "discount": {
                    "values": [0.999]
                },
                "nbr_neurone_first_layer": {
                    "values": [500]
                },
                "nbr_neurone_second_layer": {
                    "values": [500]
                },
            }
        }
        sweep_id = wandb.sweep(sweep=sweep_configs, project="sweeps_4_job")
        wandb.agent(sweep_id=sweep_id, function=train_model, count=12)
        