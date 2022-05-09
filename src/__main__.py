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


def train_model(wandb_activate = True,sweep = True, load = False):
    
    memoire = []
    
    
    with open("src/config.json") as json_file:
            configs = json.load(json_file)
    
    
    agent_type = configs["agent_type"]
    
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
    learning_rate_min = configs["learning_rate_min"]
    huber_loss = configs["huber_loss"]
    horizon = configs["horizon"]
    discount = configs["discount"]
    target_update_weight  = configs["target_update_weight"]
    target_sync_frequency  = configs["NETW_UPDATE_FREQ"]
    epsilon = configs["epsilon"]
    epsilon_min = configs["epsilon_min"]
    
    multi_step = configs["multi_step"]
    
    test_every = configs["test_every"]
    save_every = configs["save_every"]
    
    nbr_test_per_max_job = configs["nbr_test_per_max_job"]
    echu_weights = configs["echu_weights"]
    no_target_weights = configs["no_target_weights"]
    
    if wandb_activate:
        if sweep:
            run = wandb.init(config = configs)    
        else:
            if load:
                run = wandb.init(
    
                  project="2_job_ddqn_weekend",
                  id = "3fao6600",
                  resume = "must",
                  entity="devantheryl",
                  notes="without reward echu",
                  config=configs,
                )
            else:
                
                run = wandb.init(
    
                  project=str(nbr_job_max)+"_job_" + agent_type+ "_weekend",
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
    
    dict_target_date = utils.generate_test_scenarios("2022-04-04 00:00:00", nbr_job_max, seed = 0)
    #dict_target_date = {"2022-04-05 00:00:00" : 1}
    environment = Environment.create(environment=TF_environment(nbr_job_max, nbr_job_to_use, nbr_operation_max, 
                                                                nbr_machines, nbr_operator, operator_vector_length,
                                                                dict_target_date,echu_weights,no_target_weights))
    
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
        
        lr_decay = learning_rate_min/learning_rate
        if agent_type == "ddqn" or agent_type == "dueling_dqn":
            agent = Agent.create(
                agent=agent_type,
                states = environment.states(),
                actions = environment.actions(),
                max_episode_timesteps = environment.max_episode_timesteps(),
                memory=memory,
                batch_size = batch_size,
                network = network,
                update_frequency = update_frequency,
                learning_rate = dict(type = 'exponential', unit = 'episodes', num_steps = int(num_episode), initial_value = learning_rate, decay_rate = lr_decay),
                #huber_loss = huber_loss,
                horizon = horizon,
                discount = discount,
                target_update_weight = target_update_weight ,
                target_sync_frequency  = target_sync_frequency,
                exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode), initial_value = epsilon, final_value = epsilon_min),
                config = dict(seed = 1),
                tracking = 'all',
                parallel_interactions  = 16
                )
            
        if agent_type == "ppo":
            agent = Agent.create(
                agent='ppo',
                states = environment.states(),
                actions = environment.actions(),
                max_episode_timesteps = environment.max_episode_timesteps(),
                batch_size = batch_size,
                network = network,
                memory=memory,
                update_frequency = update_frequency,
                learning_rate = dict(type = 'exponential', unit = 'episodes', num_steps = int(num_episode), initial_value = learning_rate, decay_rate = lr_decay),
                multi_step = multi_step,     
                subsampling_fraction = 0.9,
                discount = discount,

                exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*0.9), initial_value = epsilon, final_value = epsilon_min),
                config = dict(seed = 1),
                tracking = 'all',
                parallel_interactions  = 8,
                )
        if agent_type == "a2c" :
            agent = Agent.create(
                agent=agent_type,
                states = environment.states(),
                actions = environment.actions(),
                max_episode_timesteps = environment.max_episode_timesteps(),
                #memory=memory,
                batch_size = batch_size,
                network = network,
                update_frequency = update_frequency,
                learning_rate = dict(type = 'exponential', unit = 'episodes', num_steps = int(num_episode), initial_value = learning_rate, decay_rate = lr_decay),
                #huber_loss = huber_loss,
                horizon = "episode",
                discount = discount,
                critic = network,
                exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*0.7), initial_value = epsilon, final_value = epsilon_min),
                config = dict(seed = 1),
                tracking = 'all',
                parallel_interactions  = 8,
                )
            
        
            
    
    
    print(agent.get_architecture())
    
    summaries = np.empty((nbr_job_max * nbr_test_per_max_job,1), dtype =  object)
    target_date_test = []
    
    
    
    for i in range(1,num_episode+1):

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
            
            #memoire.append(np.hstack((old_state,actions,reward)))
        
        score_mean.append(reward_tot)
        if score_min < reward_tot:
                score_min = reward_tot
        
        if wandb_activate and not load:
            if agent_type == "ddqn" or agent_type == "dueling_dqn":
                wandb.log(
                    {
                        "score_minimum" : score_min,
                        "exploration" : tracked["agent/exploration/exploration"],
                        "learning_rate" : tracked["agent/policy_optimizer/learning_rate/learning_rate"],
                        "policy-loss" : tracked["agent/policy-loss"],
                        "policy-objective-loss" : tracked["agent/policy-objective-loss"],
                        "update-return" : tracked["agent/update-return"],
                        "reward" : reward_tot,
                        "nbr_echu" :  environment.get_env().number_echu,
                        "nbr_no_target" : environment.get_env().number_no_target
                        
                    },
                    step =step
                )
            else:
                wandb.log(
                    {
                        "score_minimum" : score_min,
                        "exploration" : tracked["agent/exploration/exploration"],
                        "reward" : reward_tot,
                        
                    },
                    step =step
                )
            

        print("episode: ", i, "  reward : ",reward_tot, "mean_reward : ", np.mean(score_mean), "score min : ", score_min)
        
        
        if i % save_every == 0 and wandb_activate:
            agent.save("model/" + run.project + "/" +  run.name +"/", '{:010d}'.format(step), format = "hdf5")
                
        if i % test_every == 0:
            
            
            test_dict_target_dates,r = test_model(agent, nbr_test_per_max_job, nbr_job_max, nbr_operation_max, nbr_machines, nbr_operator, operator_vector_length, echu_weights, no_target_weights)
            
            
            if np.shape(summaries)[1] == 1:
                for i,item in enumerate(test_dict_target_dates):
                    summaries[i,0] = str(item)

            summaries = np.append(summaries, r, axis = 1)

            
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
            job_stats = environment.get_env().get_job_stats()
            
            if wandb_activate:
                path_img = "model/" + run.project + "/" +  run.name +"/" + '{:010d}'.format(step) + ".png"
                try: 
                    utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator ,job_stats, path_img)
                except:
                    print("impossible to viusalize")
                
                    
                for key, value in job_stats.items():
                    wandb.log(
                        {
                            key + "_lead_time" : value[0],
                            key + "_nbr_echu" : value[1]                
                        },
                        step= step
                    )

                wandb.log(
                    {
                        "evaluation_return" : reward_tot     
                    },
                    step = step
                )
            else:
                try :
                    utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator, job_stats)
                except:
                    print("impossible to viusalize")
                
     
            #nbr_job_to_use = np.random.randint(nbr_job_max) + 1
            #environment = Environment.create(environment=TF_environment(nbr_job_max, nbr_job_to_use, nbr_operation_max, 
            #                                                    nbr_machines, nbr_operator, operator_vector_length,
            #                                                    dict_target_date))

            #path_img = "model/" + run.project + "/" +  run.name +"/" + '{:010d}'.format(i) + ".png"
            
            #agent.save("model/" + run.project + "/" +  run.name +"/", '{:010d}'.format(i), format = "hdf5")
        
    
    #np.savetxt("test.csv",np.array(memoire),delimiter = ';')
    
    test_dict_target_dates,r = test_model(agent, nbr_test_per_max_job, nbr_job_max, nbr_operation_max, nbr_machines, nbr_operator, operator_vector_length, echu_weights, no_target_weights, True)
    
    
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
    job_stats = environment.get_env().get_job_stats()
        
    if wandb_activate:
        path_img = "model/" + run.project + "/" +  run.name +"/" +"final" + ".png"
        try :
            utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator ,job_stats, path_img)
        except:
            print("impossible to viusalize")
        agent.save("model/" + run.project + "/" +  run.name +"/", "final", format = "hdf5")
        
        np.savetxt("model/" + run.project + "/" +  run.name +"/" + "reward_test.csv", summaries, delimiter=';', fmt="%s")
        
        for key, value in job_stats.items():
            wandb.log(
                {
                    key + "_lead_time" : value[0],
                    key + "_nbr_echu" : value[1]                
                },
                step = step
            )
        
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
            utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator, job_stats)
        except:
            print("impossible to viusalize")

        np.savetxt("reward_test.csv", summaries, delimiter=';', fmt="%s")
                 
    agent.close()
    environment.close()
    
def test_model(agent , nbr_test_per_max_job, nbr_job_max, nbr_operation_max, nbr_machines, nbr_operator, operator_vector_length, echu_weights, no_target_weights, display = False):
    
    start_date = "2022-04-04 00:00:00"

    reward_vector = np.empty((nbr_job_max*nbr_test_per_max_job,1))
    dict_target_dates = np.empty((nbr_job_max*nbr_test_per_max_job,1), dtype = dict)
    
    index = 0
    for i in range(nbr_job_max):
        for j in range(nbr_test_per_max_job):
            #on genere i+1 target date avec leur formulation
            dict_target_date = utils.generate_test_scenarios(start_date, i+1, j)
            
            #on crée l'environnement avec i+1 nbr job max to use
            environment = Environment.create(environment=TF_environment(nbr_job_max, i+1, nbr_operation_max, 
                                                                        nbr_machines, nbr_operator, operator_vector_length,
                                                                        dict_target_date, echu_weights, no_target_weights))
            states = environment.reset()
            internals = agent.initial_internals()
            terminal = False
            reward_tot = 0
        
            while not terminal:
                # Episode timestep
                actions, internals = agent.act(states=states, internals = internals, independent=True)
                states, terminal, reward = environment.execute(actions=actions)
                
                
                reward_tot += reward
                
            
            print(reward_tot, " for test ",index, "  with ", i+1, " job")
            reward_vector[index,0] = reward_tot
            dict_target_dates[index,0] = dict_target_date
            index += 1
            
            if display:
                planning = environment.get_env().get_gant_formated()  
                job_stats = environment.get_env().get_job_stats()
                try :
                    utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator ,job_stats, "test/" + str(nbr_job_max) + "_" + str(i+1)+"_"+str(j+1))
                except:
                    print("impossible to viusalize")
            
            
    return dict_target_dates, reward_vector
            
    


def use_model(model_path, model_name, target_date, nbr_job_max):
    
    environment = Environment.create(environment=TF_environment(nbr_job_max, len(target_date), 15, 
                                                                8, 12, 7,
                                                                target_date, independent = True))
    
    agent = Agent.load(
            directory = model_path, 
            filename = model_name, 
            environment = environment,
            )
    
    states = environment.reset()
    internals = agent.initial_internals()
    terminal = False
    reward_tot = 0

    while not terminal:
        # Episode timestep
        actions, internals = agent.act(states=states, internals = internals, independent=True)
        states, terminal, reward = environment.execute(actions=actions)
        
        
        reward_tot += reward
        
    print("reward tot : ", "  reward : ", str(reward_tot))
    planning = environment.get_env().get_gant_formated()
    
    
    path_img = "output/" + "output.png"
    try: 
        utils.visualize(planning,environment.get_env().historic_time,environment.get_env().historic_operator,path_img)
    except:
        pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Program options')
    parser.add_argument('-train', dest = 'train', action = 'store_true', help = 'Train the model given the paramters in config.json')
    parser.add_argument('-wandb', dest = 'wandb_activate', action = 'store_true' , help = 'Use the wandb framework to save the hyperparameters')
    parser.add_argument('-sweep', dest = 'sweep', action = 'store_true' , help = 'Launch a bayesian hyperparameters search process over the range of parameters in config.json')
    parser.add_argument('-load', dest = 'load', action = 'store_true' , help = 'load a pretrained NN weights and biases')
    parser.add_argument('-use', dest = 'use', action = 'store_true', help = 'use the model')
    
    args = parser.parse_args()
    
    start = time.time()
    
    print("Begin of the training phase")
    
    if args.train:
        print("train model")
        train_model(args.wandb_activate,False,args.load)
        
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
                "batch_size": 32,
                "n_episode": 2000,
                
                "UPDATE_FREQ": 2,
                "target_update_weight" : {
                    "min" : 0.01,
                    "max" : 1.0
                    
                    },
                "NETW_UPDATE_FREQ": 50,
                "epsilon": 0.5,
                "epsilon_min": 0.05,  
                
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
    
    if args.use:
        print("use model")
        directory = "model/5_job_ddqn_weekend/toasty-lake-27"
        filename = "final.hdf5"
        
        target_date = {
            
            "2022-04-05 00:00:00" : 6,
            "2022-04-11 00:00:00" : 6,
            "2022-04-18 00:00:00" : 6,
            "2022-04-27 00:00:00" : 1,
            "2022-05-03 00:00:00" : 3,
            

        }
        
        use_model(directory, filename, target_date, 5)
        