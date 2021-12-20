import numpy as np
import pandas as pd 
from importlib import reload
import matplotlib.pyplot as plt
import matplotlib as mpl
import json
import random 
import time
from collections import deque

from src.Machine2 import Machine
from src.Job2 import Job
from src.Operation2 import Operation
from src.Agent2 import Agent
from src.Production_line2 import Production_line
import src.utils as utils

import matplotlib.pyplot as plt


from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Dense, Embedding, Reshape
from tensorflow.keras.optimizers import Adam

import wandb

config = {
    "nbr_job_max" : 1,
    "nbr_operation_max" : 14,
    "nbr_machines" : 14,
    "nbr_operator" : 12,
    
    "batch_size" : 64,
    "n_episode" : 2000,
    "n_epsiode_test" : 10,
    "UPDATE_FREQ" : 32,
    "NETW_UPDATE_FREQ" : 100,
    
    "params_agent" : {
        "memory" : 20000,
        "gamma" : 0.99,
        "epsilon" : 1.0,
        "epsilon_decay" : 0.9992,
        "epsilon_min" : 0.1,
        
        "learning_rate" : 0.001,
        
        
        "model" : {
            "nbr_neurone_first_layer" : 200,
            "activation_first_layer" : "relu",
            "nbr_neurone_second_layer" : 100,
            "activation_second_layer" : "relu",
            "output_layer_activation" : "linear", 
            "loss" : "huber_loss",
            "optimizer" : "Adam"
        }
    }
  
}


#prod line parameters
nbr_job_max = config["nbr_job_max"]
nbr_operation_max = config["nbr_operation_max"]
nbr_machines = config["nbr_machines"]
nbr_operator = config["nbr_operator"]


#agent parameters
batch_size = config["batch_size"]

n_episode = config["n_episode"]
UPDATE_FREQ = config["UPDATE_FREQ"]
NETW_UPDATE_FREQ = config["NETW_UPDATE_FREQ"]

wandb_activate = True
if wandb_activate:
    wandb.init(
      project="auto_scheduler",
      entity="devantheryl",
      notes="tuning hyperparamters",
      config=config,
    )


loop_number = 0
action_taken_number = 0


prod_line = Production_line(nbr_job_max, nbr_operation_max, nbr_machines, nbr_operator)
job1 = Job("TEST1", 1,20000, nbr_operation_max)
job2 = Job("TEST2", 1,20000, nbr_operation_max)
job3 = Job("TEST3", 1,20000, nbr_operation_max)

prod_line.add_job(job1)
prod_line.add_job(job2)
prod_line.add_job(job3)

agent = Agent(prod_line.state_size, len(prod_line.actions_space), config["params_agent"])
score_mean = deque(maxlen = 100)
to_plot = []

start = time.time()


actions_space = prod_line.actions_space
for e in range(n_episode):
    prod_line = Production_line(nbr_job_max, nbr_operation_max, nbr_machines, nbr_operator)
    job1 = Job("TEST1", 1,20000, nbr_operation_max)
    prod_line.add_job(job1)
    
    state = prod_line.get_state()
    done = False
    score = 0
    
    while not done:
        mask = prod_line.get_mask()
        action = agent.act(state,mask)
        action_taken_number +=1
        next_state, reward, done = prod_line.step(action)
        
        agent.remember(state, action, reward, next_state, done)
        
        state = next_state
            
        score += reward
        
        
        if loop_number % UPDATE_FREQ == 0 and loop_number > batch_size:
            history = agent.replay(batch_size)
            if wandb_activate:
                wandb.log({"loss_fit" : history.history["loss"][0]},step =e)
            
                
            pass
            
        if loop_number % NETW_UPDATE_FREQ == 0:
            
            agent.alighn_target_model()
            
        loop_number += 1
        if done:
            print("episode : {}/{}, score : {}, e : {:.2}".format(e, n_episode, score, agent.epsilon))
            score_mean.append(score)
            
            break
        
            
    print("score mean over 100 episode : " ,np.mean(score_mean))
    to_plot.append(np.mean(score_mean))
    agent.update_epsilon(e,n_episode)
    if wandb_activate:
        wandb.log({"score_mean" : np.mean(score_mean),"epsilon" : agent.epsilon},step =e)
    

print('It took', (time.time()-start)/n_episode, 'seconds.')




agent.set_test_mode(True)

sum_rewards = 0.0

n_episode_test = config["n_epsiode_test"]
for _ in range(n_episode_test):
    prod_line = Production_line(nbr_job_max, nbr_operation_max, nbr_machines, nbr_operator)
    job1 = Job("TEST1", 1,20000, nbr_operation_max)
    prod_line.add_job(job1)
    
    state = prod_line.get_state()
    done = False
    while not done:
        mask = prod_line.get_mask()
        action = agent.act(state,mask)
        next_state, reward, done = prod_line.step(action)
        
        agent.remember(state, action, reward, next_state, done)
        
        state = next_state
            
        sum_rewards += reward
        
    print(sum_rewards)
print('Mean evaluation return:', sum_rewards / n_episode_test)
wandb.run.summary['Mean evaluation return:'] = sum_rewards / n_episode_test


planning = prod_line.get_gant_formated()

#utils.visualize(planning)

