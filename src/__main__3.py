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
from tensorforce import Environment, Runner, Agent
from pandas.tseries.offsets import DateOffset


import utils as utils
os.environ["WANDB_AGENT_MAX_INITIAL_FAILURES"]= "30"

REQUIRED_PYTHON = "3.8.5"


def train_model(wandb_activate = True,sweep = True, load = False):
        
    with open("src/config.json") as json_file:
            configs = json.load(json_file)
    
    
    agent_type = configs["agent_type"]
    nbr_job_to_use = configs["nbr_job_to_use"]
    nbr_operation_max = configs["nbr_operation_max"]
    nbr_machines = configs["nbr_machines"]
    nbr_operator = configs["nbr_operator"]
    operator_vector_length = configs["operator_vector_length"]
    
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
    
    echu_weights = configs["echu_weights"]
    
    if wandb_activate:
        if sweep:
            run = wandb.init(config = configs)    
        else:
            if load:
                run = wandb.init(
    
                  project="5_job_ddqn_weekend",
                  id = "14iprn20",
                  resume = "must",
                  entity="devantheryl",
                  notes="without reward echu",
                  config=configs,
                )
            else:
                
                run = wandb.init(
    
                  project="reccurent" + "_job_" + agent_type+ "_weekend",
                  entity="devantheryl",
                  notes = "only 6 formu",
                  config=configs,
                )
        
        
        os.makedirs("model/" + run.project, exist_ok=True)
        os.makedirs("model/" + run.project + "/" + run.name, exist_ok = True)
        print(run.name)
        print(run.project)
        
    score_mean_tot = deque(maxlen = 300)
    score_mean_batch = deque(maxlen = 300)
    score_max_batch = -1000
    score_max_tot = -1000
    
    target = "2022-04-04 00:00:00"
    target = pd.to_datetime(target)
    formulation = 1
    job_name = "TEST0"
    #dict_target_date = {"2022-04-05 00:00:00" : 1}
    environment = Environment.create(environment = TF_environment(target, formulation, job_name, nbr_operation_max, nbr_machines, nbr_operator, 
                                                                  operator_vector_length,None, echu_weights = echu_weights, independent =False))
    
    #AGENT CREATION
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
            learning_rate = dict(type = 'exponential', unit = 'episodes', num_steps = int(num_episode*nbr_job_to_use), initial_value = learning_rate, decay_rate = lr_decay),
            #huber_loss = huber_loss,
            horizon = horizon,
            discount = discount,
            target_update_weight = target_update_weight ,
            target_sync_frequency  = target_sync_frequency,
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
        for j in range(nbr_job_to_use):
            # Initialize episode
            environment.job_name = "JOB" + str(j)
            environment.target = target
            environment.formulation = formulation 
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
            
            if target.dayofweek == 0:
                rdm_day = np.random.choice([7,8,9,10], 1)[0]
            if target.dayofweek == 1:
                rdm_day = np.random.choice([6,7,8,9], 1)[0]
            if target.dayofweek == 2:
                rdm_day = np.random.choice([5,6,7,8], 1)[0]
            if target.dayofweek == 3:
                rdm_day = np.random.choice([4,5,6,7], 1)[0]
                
            target += DateOffset(days = int(rdm_day))
            formulation = np.random.choice([1,3,6],1,p =[0.25,0.25,0.5])[0]
            
            #LOG all value for 1 batch episode
            if wandb_activate:
            
                wandb.log(
                    {
                        "exploration" : tracked["agent/exploration/exploration"],
                        "learning_rate" : tracked["agent/policy_optimizer/learning_rate/learning_rate"],
                        "policy-loss" : tracked["agent/policy-loss"],
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
        
        
        
        
        if i % save_every == 0 and wandb_activate:
            agent.save("model/" + run.project + "/" +  run.name +"/", '{:010d}'.format(step), format = "hdf5")
                
        if i % test_every == 0:
            
            #test for 1 episode
            planning_tot = None
            reward_tot = 0
            futur_state = None
            
            
            for j in range(nbr_job_to_use):
                # Initialize episode
                print(target, formulation)
                environment.job_name = "JOB" + str(j)
                environment.target = target
                environment.formulation = formulation 
                environment.futur_state = futur_state
                states = environment.reset()
                internals = agent.initial_internals()
                terminal = False
                reward_batch = 0
                
                while not terminal:
                    # Episode timestep
                    actions, internals = agent.act(states=states, internals = internals, independent=True)
                    states, terminal, reward = environment.execute(actions=actions)
        
                    reward_batch += reward
                    
                futur_state = environment.get_env().state_full
                reward_tot += reward_batch
                
                if target.dayofweek == 0:
                    rdm_day = np.random.choice([7,8,9,10], 1)[0]
                if target.dayofweek == 1:
                    rdm_day = np.random.choice([6,7,8,9], 1)[0]
                if target.dayofweek == 2:
                    rdm_day = np.random.choice([5,6,7,8], 1)[0]
                if target.dayofweek == 3:
                    rdm_day = np.random.choice([4,5,6,7], 1)[0]
                    
                target += DateOffset(days = int(rdm_day))
                formulation = np.random.choice([1,3,6],1,p =[0.25,0.25,0.5])[0]
                
                
                planning = environment.get_env().get_gant_formated()
                planning_tot  = pd.concat([planning_tot,planning])
            
                
            historic_time_tot = (futur_state.index.to_series()).tolist()
            historic_operator_tot = futur_state["operator"].tolist()
                
            print("test at epsiode : ", str(i), "  reward : ", str(reward_tot))

            
            if wandb_activate:
                path_img = "model/" + run.project + "/" +  run.name +"/" + '{:010d}'.format(step) + ".png"
                try: 
                    utils.visualize(planning_tot,historic_time_tot,historic_operator_tot, path_img)
                except:
                    print("impossible to viusalize")

                wandb.log(
                    {
                        "evaluation_return" : reward_tot     
                    },
                    step = step
                )
            else:
                try :
                    utils.visualize(planning_tot,historic_time_tot,historic_operator_tot)
                except:
                    print("impossible to viusalize")
                    
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
        print("sweep model")
    
    if args.use:
        print("use model")
        directory = "model/5_job_ddqn_weekend/fine-capybara-38"
        filename = "final.hdf5"
        
        target_date = {
            
            "2022-04-05 00:00:00" : 6,
            "2022-04-11 00:00:00" : 6,
            "2022-04-18 00:00:00" : 6,
            "2022-04-27 00:00:00" : 1,

            
        }
        
        use_model(directory, filename, target_date, 4)
        