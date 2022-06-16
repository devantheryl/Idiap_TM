import numpy as np
import pandas as pd
import sys
import os
import time
import argparse
import json
from collections import deque
import wandb

from src.TF_env3 import TF_environment
from src.test_model import evaluate_model
from tensorforce import Environment, Runner, Agent
from pandas.tseries.offsets import DateOffset


import utils as utils
os.environ["WANDB_AGENT_MAX_INITIAL_FAILURES"]= "30"

REQUIRED_PYTHON = "3.8.5"


def train_model(wandb_activate = True,sweep = True, load = False):
        
    with open("src/config.json") as json_file:
            configs = json.load(json_file)
    
    
    agent_type = "ddqn"
    if wandb_activate:
        if sweep:
            run = wandb.init()    
        else:
            if load:
                run = wandb.init(
    
                  project="Evaluation_DQN",
                  id = "14iprn20",
                  resume = "must",
                  entity="devantheryl",
                  notes="without reward echu",
                  config=configs,
                )
            else:
                
                run = wandb.init(
    
                  project="reccurent" + "_job_" + agent_type+ "_weekend__sweep",
                  entity="devantheryl",
                  notes = "only 6 formu",
                  config=configs,
                )
        
        config = wandb.config
        os.makedirs("model/" + run.project, exist_ok=True)
        os.makedirs("model/" + run.project + "/" + run.name, exist_ok = True)
        print(run.name)
        print(run.project)
        
        

        nbr_operation_max = 15
        nbr_machines = 8
        nbr_operator = 12
        
        memory = 500000
        batch_size = 256
        update_frequency = 2
        
        nbr_job_to_use = config.nbr_job_to_use
        num_episode = int(700/nbr_job_to_use)
        operator_vector_length = config.ressource_states_len
        echu_weights = config.echu_weights
        forward_weights = config.forward_weights
        ordo_weights = config.ordo_weights
        job_finished_weigths = config.job_finished_weigths
        
        nbr_neurones = config.nbr_neurones
        nbr_layers = config.nbr_layers
        activation_function = config.activation_function
        
        learning_rate = config.learning_rate
        horizon = config.horizon
        discount = config.discount
        target_sync_frequency  = config.target_sync_frequency
        epsilon = config.epsilon
        epsilon_min = config.epsilon_min
        
        
        test_every = 1000
        save_every = 10000
        network = []
        for i in range(nbr_layers):
            network.append(dict(type = "dense", size = nbr_neurones, activation = activation_function))
                    
        
        
        
        
    score_mean_tot = deque(maxlen = 300)
    score_mean_batch = deque(maxlen = 300)
    score_max_batch = -1000
    score_max_tot = -1000
    
    target = "2022-04-04 00:00:00"
    target = pd.to_datetime(target)
    formulation = 1
    echelle = 20000
    job_name = "TEST0"
    #dict_target_date = {"2022-04-05 00:00:00" : 1}
    environment = Environment.create(environment = TF_environment(target, formulation,echelle, job_name, nbr_operation_max, nbr_machines, nbr_operator, 
                                                                  operator_vector_length,None, echu_weights = echu_weights,
                                                                  forward_weights = forward_weights, ordo_weights = ordo_weights,
                                                                  job_finished_weigths = job_finished_weigths, independent =False))
    
    #AGENT CREATION

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
            learning_rate = learning_rate,
            #huber_loss = huber_loss,
            horizon = horizon,
            discount = discount,
            target_update_weight = 1.0 ,
            target_sync_frequency  = target_sync_frequency,
            exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*nbr_job_to_use), initial_value = epsilon, final_value = epsilon_min),
            config = dict(seed = 1),
            tracking = 'all',
            parallel_interactions  = 16
        )
    if agent_type == "a2c":
        agent = Agent.create(
            agent=agent_type,
            states = environment.states(),
            actions = environment.actions(),
            max_episode_timesteps = environment.max_episode_timesteps(),
            batch_size = batch_size,
            network = network,
            update_frequency = update_frequency,
            learning_rate = learning_rate,
            #l2_regularization = huber_loss,
            horizon = horizon,
            discount = discount,
            critic = network,
            exploration = dict(type = 'linear', unit = 'episodes', num_steps = int(num_episode*nbr_job_to_use), initial_value = epsilon, final_value = epsilon_min),
            config = dict(seed = 1),
            tracking = 'all',
            parallel_interactions  = 16
        )
    print(agent.get_architecture())


    #BEGIN OF THE TRAINING PHASE
    planning_tot = None
    step = 0
    
    
    for i in range(1,num_episode+1): 
        
        reward_tot = 0
        futur_state = None
        target = "2022-04-04 00:00:00"
        target = pd.to_datetime(target)
        planning_tot = None
        for j in range(nbr_job_to_use):
            
            
            # Initialize episode
            
            environment.job_name = "JOB" + str(j)
            environment.target = target
            environment.formulation = formulation 
            environment.echelle = echelle
            
            
            environment.futur_state = futur_state
            states = environment.reset()
            reward_batch = 0
            terminal = False
            
            while not terminal:
                # Episode timestep
    
                actions = agent.act(states=states, independent = False)
                
                
                states, terminal, reward = environment.execute(actions=actions)
                
                agent.observe(terminal=terminal, reward=reward)
    
                reward_batch += reward
                tracked = agent.tracked_tensors()      
                
                step+=1
                
            futur_state = environment.get_env().state_full
            reward_tot += reward_batch
                
            
                
            ################DEBUG#############################
            planning = environment.get_env().get_gant_formated()
            planning_tot  = pd.concat([planning_tot,planning])
            historic_time_tot = (futur_state.index.to_series()).tolist()
            historic_operator_tot = futur_state["operator"].tolist()
            ##################################################
            
            if target.dayofweek == 0:
                rdm_day = np.random.choice([7,8,9,3], 1)[0]
            if target.dayofweek == 1:
                rdm_day = np.random.choice([6,7,8], 1)[0]
            if target.dayofweek == 2:
                rdm_day = np.random.choice([5,6,7], 1)[0]
            if target.dayofweek == 3:
                rdm_day = np.random.choice([5,6], 1)[0]
                
            target += DateOffset(days = int(rdm_day))
            formulation = np.random.choice([1,3,6],1,p =[0.25,0.25,0.5])[0]
            echelle = np.random.choice([20000,6600], p = [0.9,0.1])
            
            #LOG all value for 1 batch episode
            if wandb_activate:
                if agent_type == "ddqn":
                    wandb.log(
                        {
                            "exploration" : tracked["agent/exploration/exploration"],
                            "policy-loss" : tracked["agent/policy-loss"],
                            "update-return" : tracked["agent/update-return"],
                            "reward_batch" : reward_batch,
                            "lead_time" : environment.get_env().job.lead_time
                        },
                        step =step
                    )
                if agent_type == "a2c":
                    wandb.log(
                        {
                            "baseline-loss" : tracked["agent/baseline-loss"],
                            "baseline-objective-loss" : tracked["agent/baseline-objective-loss"],
                            "baseline-regularization-loss" : tracked["agent/baseline-regularization-loss"],
                            "entropy" : tracked["agent/entropy"],
                            "exploration" : tracked["agent/exploration/exploration"],
                            "agent/kl-divergence" : tracked["agent/kl-divergence"],
                            "policy-loss" : tracked["agent/policy-loss"],
                            "policy-objective-loss" : tracked["agent/policy-objective-loss"],
                            "policy-regularization-loss" : tracked["agent/policy-regularization-loss"],                 
                            "learning_rate" : tracked["agent/policy_optimizer/learning_rate/learning_rate"],
                            "update-advantage" : tracked["agent/update-advantage"],
                            "update-return" : tracked["agent/update-return"],
                            "reward_batch" : reward_batch,
                            "lead_time" : environment.get_env().job.lead_time
                        },
                        step =step
                    )
            if score_max_batch < reward_batch:
                score_max_batch = reward_batch
            score_mean_batch.append(reward_batch)
            print("episode: ", (i-1)*nbr_job_to_use+(j+1), "  reward_batch : ",reward_batch, "mean_reward_batch: ", np.mean(score_mean_batch), "score max batch : ", score_max_batch)
            
            
        score_mean_tot.append(reward_tot)
        if score_max_tot < reward_tot:
                score_max_tot = reward_tot  
        print("reward_tot : ",reward_tot, "mean_reward_tot : ", np.mean(score_mean_tot), "score max tot : ", score_max_tot)
                
        if wandb_activate:
            
            wandb.log(
                {
                    "score_max" : score_max_tot,
                    "reward_tot" : reward_tot,
                },
                step =step
            )
        
        
                
        
            
    nbr_done, completion_rate, min_delta, max_delta, mean_delta, std_delta, sum_delta, reward_tot = evaluate_model(agent, environment, operator_vector_length, echu_weights)

    
    if wandb_activate:
        wandb.log(
            {
                "nbr_done" : nbr_done,
                "completion_rate" : completion_rate, 
                "min_delta" : min_delta, 
                "max_delta": max_delta, 
                "mean_delta" : mean_delta, 
                "std_delta" : std_delta, 
                "sum_delta" : sum_delta, 
                "reward_tot" : reward_tot
            },
            step = step
        )
    print("number done : ", nbr_done)
    print("completion_rate : ", completion_rate)
    print("min_delta : ", min_delta)
    print("max_delta : ", max_delta)
    print("mean_delta : ", mean_delta)
    print("std_delta : ", std_delta)
    print("sum_delta : ", sum_delta)
                    
    if wandb_activate:
        
        run.finish()
        
    agent.close()
    environment.close()

            
    


def use_model(model_path, model_name, target_date, nbr_job_max):
    
    environment = Environment.create(environment=TF_environment(nbr_job_max, len(target_date), 15, 
                                                                8, 12, 28,
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
        sweep_configs = {
            "name" : "my_sweep",
            "project" : "sweep_4_job",
            "entity" : "devantheryl",
            "method": "bayes",
            "metric": {
                "name": "completion_rate",
                "goal": "maximize",
            },
            "parameters": {
                "nbr_job_to_use": {
                    "min": 1,
                    "max" : 8
                },
                "ressource_states_len": {
                    "min": 2,
                    "max" : 28
                },
                "echu_weights": {
                    "min": -100,
                    "max" : 0
                },
                "forward_weights": {
                    "min": -1,
                    "max" : 0
                },
                "ordo_weights": {
                    "min": 0,
                    "max" : 10
                },
                "job_finished_weigths": {
                    "min": 0,
                    "max" : 100
                },
                "nbr_neurones": {
                    "min": 32,
                    "max" : 512
                },
                "nbr_layers": {
                    "min": 1,
                    "max" : 5
                },
                "activation_function": {
                    "values" : ["relu", "tanh", "sigmoid"]
                },
                "learning_rate": {
                    "min": 0.00001,
                    "max" : 0.01
                },
                "horizon": {
                    "min": 1,
                    "max" : 100
                },
                "discount": {
                    "min": 0.1,
                    "max" : 0.9999
                },
                "target_sync_frequency": {
                    "min": 20,
                    "max" : 400
                },
                "epsilon": {
                    "min": 0.5,
                    "max" : 0.99
                },
                "epsilon_min": {
                    "min": 0.05,
                    "max" : 0.4
                },
            }
        }
        sweep_id = wandb.sweep(sweep=sweep_configs, project="DQN_hyperparametersTuning")
        wandb.agent(sweep_id=sweep_id, function=train_model, count=200)
        