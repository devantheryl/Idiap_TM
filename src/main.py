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

import os


from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Dense, Embedding, Reshape
from tensorflow.keras.optimizers import Adam

import wandb

with open("src/config") as json_file:
    config = json.load(json_file)




#agent parameters
batch_size = config["batch_size"]

n_episode = config["n_episode"]
UPDATE_FREQ = config["UPDATE_FREQ"]
NETW_UPDATE_FREQ = config["NETW_UPDATE_FREQ"]

wandb_activate = True
if wandb_activate:
    run = wandb.init(
      project="auto_scheduler_4jobs",
      entity="devantheryl",
      notes="tuning hyperparamters",
      config=config,
    )
    os.makedirs("model/" + run.project, exist_ok=True)
    os.makedirs("model/" + run.project + "/" + run.name, exist_ok=True)
    print(run.name)
    print(run.project)




loop_number = 0
action_taken_number = 0

prod_line = Production_line()
agent = Agent(prod_line.state_size, len(prod_line.actions_space), config["params_agent"])
score_mean = deque(maxlen = 100)
score_min = -10000
to_plot = []

start = time.time()


actions_space = prod_line.actions_space
for e in range(n_episode):
    prod_line = Production_line()
    #job1 = Job("TEST1", 1,20000, nbr_operation_max)
    #job2 = Job("TEST2", 1,20000, nbr_operation_max)
    #job3 = Job("TEST3", 1,20000, nbr_operation_max)
    #job4 = Job("TEST4", 1,20000, nbr_operation_max)
    #job5 = Job("TEST5", 1,20000, nbr_operation_max)
    #job6 = Job("TEST6", 1,20000, nbr_operation_max)
    #job7 = Job("TEST7", 1,20000, nbr_operation_max)
    #job8 = Job("TEST8", 1,20000, nbr_operation_max)
    #job9 = Job("TEST9", 1,20000, nbr_operation_max)
    #job10 = Job("TEST10", 1,20000, nbr_operation_max)
    #job11 = Job("TEST11", 1,20000, nbr_operation_max)
    #job12 = Job("TEST12", 1,20000, nbr_operation_max)
    #job13 = Job("TEST13", 1,20000, nbr_operation_max)
    #job14 = Job("TEST14", 1,20000, nbr_operation_max)
    
    #prod_line.add_job(job1)
    #prod_line.add_job(job2)
    #prod_line.add_job(job3)
    #prod_line.add_job(job4)
    #prod_line.add_job(job5)
    #prod_line.add_job(job6)
    #prod_line.add_job(job7)
    #prod_line.add_job(job8)
    #prod_line.add_job(job9)
    #prod_line.add_job(job10)
    #prod_line.add_job(job11)
    #prod_line.add_job(job12)
    #prod_line.add_job(job13)
    #prod_line.add_job(job14)

    
    
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
            if score_min < score:
                score_min = score
            
            break
        
            
    print("score mean over 100 episode : " ,np.mean(score_mean))
    to_plot.append(np.mean(score_mean))
    agent.update_epsilon(e,n_episode)
    if wandb_activate:
        wandb.log({"score_mean" : np.mean(score_mean),"epsilon" : agent.epsilon},step =e)
        
    if e%500 == 0 and e > 0:
        
        agent.save("model/" + run.project + "/" +  run.name +"/"+ '{:010d}'.format(e) + ".hdf5")
        pass

agent.save("model/" + run.project + "/" +  run.name +"/"+ "final" + ".hdf5")



agent.set_test_mode(True)

sum_rewards = 0.0
max_episode = 1000

n_episode_test = config["n_epsiode_test"]
for _ in range(n_episode_test):
    prod_line = Production_line()
    #job1 = Job("TEST1", 1,20000, nbr_operation_max)
    #job2 = Job("TEST2", 1,20000, nbr_operation_max)
    #job3 = Job("TEST3", 1,20000, nbr_operation_max)
    #job4 = Job("TEST4", 1,20000, nbr_operation_max)
    #job5 = Job("TEST5", 1,20000, nbr_operation_max)
    #job6 = Job("TEST6", 1,20000, nbr_operation_max)
    #job7 = Job("TEST7", 1,20000, nbr_operation_max)
    #job8 = Job("TEST8", 1,20000, nbr_operation_max)
    #job9 = Job("TEST9", 1,20000, nbr_operation_max)
    #job10 = Job("TEST10", 1,20000, nbr_operation_max)
    #job11 = Job("TEST11", 1,20000, nbr_operation_max)
    #job12 = Job("TEST12", 1,20000, nbr_operation_max)
    #job13 = Job("TEST13", 1,20000, nbr_operation_max)
    #job14 = Job("TEST14", 1,20000, nbr_operation_max)
    
    #prod_line.add_job(job1)
    #prod_line.add_job(job2)
    #prod_line.add_job(job3)
    #prod_line.add_job(job4)
    #prod_line.add_job(job5)
    #prod_line.add_job(job6)
    #prod_line.add_job(job7)
    #prod_line.add_job(job8)
    #prod_line.add_job(job9)
    #prod_line.add_job(job10)
    #prod_line.add_job(job11)
    #prod_line.add_job(job12)
    #prod_line.add_job(job13)
    #prod_line.add_job(job14)
    
    state = prod_line.get_state()
    done = False
    nbr_passage = 0
    while not done :
        mask = prod_line.get_mask()
        action = agent.act(state,mask)
        next_state, reward, done = prod_line.step(action)
        
        state = next_state
            
        sum_rewards += reward
        nbr_passage += 1
        if nbr_passage > max_episode:
            break
        
        
    print(sum_rewards)
print('Mean evaluation return:', sum_rewards / n_episode_test)
if wandb_activate:
    wandb.run.summary['Mean evaluation return:'] = sum_rewards / n_episode_test
    wandb.run.summary["score_minimum"] = score_min


planning = prod_line.get_gant_formated()
print(planning)
utils.visualize(planning)

