# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 10:12:59 2022

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

def train_model(wandb_activate = True,sweep = True, load = False):
    
    memoire = []
    
    with open("src/config.json") as json_file:
            configs = json.load(json_file)
    
    nbr_job_max = configs["nbr_job_max"]
    nbr_job_to_use = configs["nbr_job_to_use"]
    nbr_operation_max = configs["nbr_operation_max"]
    nbr_machines = configs["nbr_machines"]
    nbr_operator = configs["nbr_operator"]
    operator_vector_length = configs["operator_vector_length"]
    dict_target_date = configs["target_date"]
    
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
    
    test_every = configs["test_every"]
    save_every = configs["save_every"]
    
    
    if wandb_activate:
        if sweep:
            run = wandb.init(config = configs)    
        else:
            if load:
                run = wandb.init(
    
                  project="8_job_ddqn_weekend",
                  id = "3fao6600",
                  resume = "must",
                  entity="devantheryl",
                  notes="without reward echu",
                  config=configs,
                )
            else:
                
                run = wandb.init(
    
                  project="9_job_ddqn_weekend",
                  entity="devantheryl",
                  notes = "",
                  config=configs,
                )
        
        
        os.makedirs("model/" + run.project, exist_ok=True)
        os.makedirs("model/" + run.project + "/" + run.name, exist_ok = True)
        print(run.name)
        print(run.project)
        
        
    
    
    score_mean = deque(maxlen = 300)
    score_min = -10000
    
    
    environment = Environment.create(environment=TF_environment(nbr_job_max, nbr_job_to_use, nbr_operation_max, 
                                                                nbr_machines, nbr_operator, operator_vector_length,
                                                                dict_target_date))
    
    step = 0
    
    if load:
        agent = Agent.load(
            directory = "model/8_job_ddqn_weekend/lunar-snowflake-2/", 
            filename = "0000011000.hdf5", 
            environment = environment,
            #learning_rate = 0.0001,
            #tracking = 'all',
            #exploration = 0.9,
        )
        step = 3043659
    else: 
        
        lr_decay = np.log()
        agent = Agent.create(
            agent='ddqn',
            states = environment.states(),
            actions = environment.actions(),
            max_episode_timesteps = environment.max_episode_timesteps(),
            memory=memory,
            batch_size = batch_size,
            network = network,
            update_frequency = update_frequency,
            learning_rate = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*0.8), initial_value = 0.001, final_value = learning_rate),
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
    
    for i in range(num_episode):

        # Initialize episode
        states = environment.reset()
        terminal = False
        reward_tot = 0
        
        while not terminal:
            # Episode timestep

            actions = agent.act(states=states, independent = False)
            
            old_state = states["state"]
            states, terminal, reward = environment.execute(actions=actions)
            
            agent.observe(terminal=terminal, reward=reward)
            reward_tot += reward
            tracked = agent.tracked_tensors()
            
            step+=1
            
            #memoire.append(np.hstack((old_state,actions,reward,terminal)))
        
        
        if wandb_activate and not load:
            wandb.log(
                {
                    "score_minimum" : score_min,
                    "exploration" : tracked["agent/exploration/exploration"],
                    "learning_rate" : tracked["agent/policy_optimizer/learning_rate/learning_rate"],
                    "policy-loss" : tracked["agent/policy-loss"],
                    "policy-objective-loss" : tracked["agent/policy-objective-loss"],
                    "update-return" : tracked["agent/update-return"],
                    "reward" : reward_tot,
                    
                },
                step =step
            )
            
            
        score_mean.append(reward_tot)
        if score_min < reward_tot:
                score_min = reward_tot
                
        print("episode: ", i, "  reward : ",reward_tot, "mean_reward : ", np.mean(score_mean), "score min : ", score_min)
        
        
        if i % save_every == 0 and wandb_activate:
            agent.save("model/" + run.project + "/" +  run.name +"/", '{:010d}'.format(step), format = "hdf5")
                
        if i % test_every == 0:
            
            #test for 1 episode
            states = environment.reset()
            internals = agent.initial_internals()
            terminal = False
            reward_tot = 0
        
            while not terminal:
                # Episode timestep
                actions, internals = agent.act(states=states, internals = internals, independent=True)
                states, terminal, reward = environment.execute(actions=actions)
                
                
                reward_tot += reward
                
            print("test at epsiode : ", str(i), "  reward : ", str(reward_tot))
            planning = environment.get_env().get_gant_formated()
            
            if wandb_activate:
                path_img = "model/" + run.project + "/" +  run.name +"/" + '{:010d}'.format(step) + ".png"
                try: 
                    utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator,path_img)
                except:
                    print("impossible to viusalize")

                wandb.log(
                    {
                        "evaluation_return" : reward_tot     
                    },
                    step = step
                )
                
                
            else:
                try: 
                    utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator)
                except:
                    print("impossible to viusalize")
                pass
            

            #path_img = "model/" + run.project + "/" +  run.name +"/" + '{:010d}'.format(i) + ".png"
            
            #agent.save("model/" + run.project + "/" +  run.name +"/", '{:010d}'.format(i), format = "hdf5")
        
    
    #np.savetxt("test.csv",np.array(memoire),delimiter = ';')
    
    states = environment.reset()
    internals = agent.initial_internals()
    terminal = False
    reward_tot = 0

    while not terminal:
        # Episode timestep
        actions, internals = agent.act(states=states, internals = internals, independent=True)
        states, terminal, reward = environment.execute(actions=actions)
        
        step+=1
        reward_tot += reward
        
    print("final result : ", reward_tot)        
    
    tracked = agent.tracked_tensors()
    planning = environment.get_env().get_gant_formated()    
        
    if wandb_activate:
        path_img = "model/" + run.project + "/" +  run.name +"/" +"final" + ".png"
        try :
            utils.visualize(planning,path_img)
        except:
            print("impossible to viusalize")
        agent.save("model/" + run.project + "/" +  run.name +"/", "final", format = "hdf5")
        
        wandb.log(
            {
                "score_minimum" : score_min,
                "evaluation_return" : reward_tot     
            },
            step = step
        )
        run.finish()
        
    else:
        try :
            utils.visualize(planning)
        except:
            print("impossible to viusalize")
                 
    agent.close()
    environment.close()
        
        
        
        
        