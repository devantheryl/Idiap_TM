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
os.environ["WANDB_AGENT_MAX_INITIAL_FAILURES"]= "30"

REQUIRED_PYTHON = "3.8.5"

def train_model(wandb_activate = True,sweep = True):
    
    memoire = []
    
    with open("src/config.json") as json_file:
            configs = json.load(json_file)
        
    if wandb_activate:
        if sweep:
            run = wandb.init(config = configs)    
        else:
            run = wandb.init(

              project="2_job_ddqn_weekend",

              entity="devantheryl",
              notes="",
              config=configs,
            )
        config = wandb.config
        
        os.makedirs("model/" + run.project, exist_ok=True)
        os.makedirs("model/" + run.project + "/" + run.name, exist_ok = True)
        print(run.name)
        print(run.project)
        
        num_episode = config.n_episode
        memory = config.memory
        batch_size = config.batch_size
        network = config.network
        update_frequency = config.UPDATE_FREQ
        learning_rate = config.learning_rate
        huber_loss = config.huber_loss
        horizon = config.horizon
        discount = config.discount
        target_update_weight  = config.target_update_weight 
        target_sync_frequency  = config.NETW_UPDATE_FREQ
        epsilon = config.epsilon
        epsilon_min = config.epsilon_min
        
    else:
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
    
    score_mean = deque(maxlen = 100)
    score_min = -10000
    
    
    environment = Environment.create(environment=TF_environment)
    
    agent = Agent.create(
        agent='ddqn',
        states = environment.states(),
        actions = environment.actions(),
        max_episode_timesteps = environment.max_episode_timesteps(),
        memory=memory,
        batch_size = batch_size,
        network = network,
        update_frequency = update_frequency,
        learning_rate = learning_rate,
        #huber_loss = huber_loss,
        horizon = horizon,
        discount = discount,
        target_update_weight = target_update_weight ,
        target_sync_frequency  = target_sync_frequency,
        exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*0.9), initial_value = epsilon, final_value = epsilon_min),
        config = dict(seed = 1),
        tracking = 'all',
        parallel_interactions  = 8,
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
            
            old_state = states["state"]
            states, terminal, reward = environment.execute(actions=actions)
            
            agent.observe(terminal=terminal, reward=reward)
            reward_tot += reward
            tracked = agent.tracked_tensors()
            step+=1
            
            memoire.append(np.hstack((old_state,actions,reward,terminal)))
        
        
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
        if reward_tot == -68:
            planning = environment.get_env().get_gant_formated()
            utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator)
        if i %100 == 0:
            planning = environment.get_env().get_gant_formated()
            if wandb_activate:
                path_img = "model/" + run.project + "/" +  run.name +"/" + '{:010d}'.format(i) + ".png"
                try: 
                    utils.visualize(planning,path_img)
                except:
                    print("impossible to viusalize")
                
                agent.save("model/" + run.project + "/" +  run.name +"/", '{:010d}'.format(i), format = "hdf5")
            else:
                #utils.visualize(planning)
                pass

            #path_img = "model/" + run.project + "/" +  run.name +"/" + '{:010d}'.format(i) + ".png"
            try: 
                utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator)
            except:
                print("impossible to viusalize")
            #agent.save("model/" + run.project + "/" +  run.name +"/", '{:010d}'.format(i), format = "hdf5")
        
    
    np.savetxt("test.csv",np.array(memoire),delimiter = ';')
    
    states = environment.reset()
    terminal = False
    reward_tot = 0

    while not terminal:
        # Episode timestep
        actions = agent.act(states=states, independent=True)
        states, terminal, reward = environment.execute(actions=actions)
        print("reward : ", reward,"  actions :", actions)
        
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
    
        
    if wandb_activate:
        path_img = "model/" + run.project + "/" +  run.name +"/" +"final" + ".png"
        try :
            utils.visualize(planning,path_img)
        except:
            print("impossible to viusalize")
        agent.save("model/" + run.project + "/" +  run.name +"/", "final", format = "hdf5")
    else:
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
            "name" : "removing limitation on deltatime reward, +1 if forward wip =0",
            "project" : "sweep_2_jobs",
            "entity" : "devantheryl",
            "method": "bayes",
            "metric": {
                "name": "evaluation_return",
                "goal": "maximize",
            },
            "parameters": {
                "batch_size": {
                    "min" : 4,
                    "max" : 1024,
                },
                "n_episode": {
                    "min" : 500,
                    "max" : 6000
                    
                },
                "UPDATE_FREQ": {
                    "min" : 2,
                    "max" : 64,
                },
                "target_update_weight" : {
                    "min" : 0.01,
                    "max" : 1.0
                    
                    },
                "NETW_UPDATE_FREQ": {
                    "min" : 2,
                    "max" : 100
                },
                "epsilon": {
                    "min" : 0.5,
                    "max" : 1.0
                },
                "epsilon_min": {
                    "min" : 0.01,
                    "max" : 0.4
                    
                },
                "learning_rate": {
                    "min" : 0.00001,
                    "max" : 0.1
                },
                "huber_loss": {
                    "min" : 0.1,
                    "max" : 10.0
                    
                },
                "horizon": {
                    "min" : 1,
                    "max" : 500
                },
                "discount": {
                    "min" : 0.1,
                    "max" : 1.0
                    
                },
                "entropy_regularization":{
                    "min" : 0,
                    "max" : 100
                    },
                "nbr_neurone_first_layer": {
                    "min" : 200,
                    "max" : 2000
                },
                "nbr_neurone_second_layer": {
                    "min" : 200,
                    "max" : 2000
                },
            }
        }
        sweep_id = wandb.sweep(sweep=sweep_configs, project="sweeps_2_job_test_reward_shaping_dueling_dqn")
        wandb.agent(sweep_id=sweep_id, function=train_model, count=50)
        