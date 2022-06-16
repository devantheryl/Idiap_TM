# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 10:18:28 2022

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

from src.TF_env3 import TF_environment
from tensorforce import Environment, Runner, Agent
from pandas.tseries.offsets import DateOffset


import src.utils as utils
os.environ["WANDB_AGENT_MAX_INITIAL_FAILURES"]= "30"

REQUIRED_PYTHON = "3.8.5"


def local_test():
    #MODEL TO USE
    directory = "model/reccurent_job_ddqn_weekend/distinctive-jazz-27"
    filename = "final.hdf5"
    
    
    #LOAD THE TEST FILE
    df = pd.read_excel("data/test_set.xlsx")
    
    formulations = np.array(df["FORMULATION"].tolist())
    targets = np.array(df["DATE DEBUT REMPLISSAGE"].tolist())
    lead_times = np.array(df["lead-time broyage->remplissage"].tolist())
    echelles = np.array(df["ECHELLE"].tolist())
    job_names = np.array(df["CODE TRANSIT."].tolist())
    
    
    
    formulations = np.array(formulations)
    formulations = np.where(formulations == 3.75, 1, formulations)
    formulations = np.where(formulations == 11.25, 3, formulations)
    formulations = np.where(formulations == 22.5, 6, formulations)
    formulations = formulations.astype(int)
    
    df["lead_time_test"] = 0
    df["done"] = False
    df["rewards"] = -100
    
    target = targets[0]
    formulation = formulations[0]
    echelle = echelles[0]
    job_name = job_names[0]
    nbr_operation_max = 15
    nbr_machines = 8
    nbr_operator = 12
    nbr_job_to_use = len(targets)
    
    #model params
    operator_vector_length = 28
    echu_weights = 0
    ordo_weights = 4
    job_finished_weigths = 0
    forward_weights = -1
    independent = True
    
    environment = Environment.create(environment = TF_environment(target, formulation,echelle, job_name, nbr_operation_max, nbr_machines, nbr_operator, 
                                                                  operator_vector_length,None, echu_weights = echu_weights,
                                                                  forward_weights = forward_weights, ordo_weights = ordo_weights,
                                                                  job_finished_weigths = job_finished_weigths, independent =False))
    
    
    agent = Agent.load(
            directory = directory, 
            filename = filename, 
            environment = environment,
            )
    
    
    
    reward_tot = 0
    futur_state = None
    planning_tot = None
    for j in range(nbr_job_to_use):
        # Initialize episode
        target = targets[j]
        formulation = formulations[j]
        echelle = echelles[j]
        job_name = job_names[j]
        
        environment.job_name = job_name
        environment.target = target
        environment.formulation = formulation 
        environment.echelle = echelle
        environment.futur_state = futur_state
        states = environment.reset()
        reward_batch = 0
        terminal = False
        internals = agent.initial_internals()
        
        while not terminal:
             # Episode timestep
            actions, internals = agent.act(states=states, internals = internals, independent=True)
            states, terminal, reward = environment.execute(actions=actions)
    
            reward_batch += reward
            
        futur_state = environment.get_env().state_full
        reward_tot += reward_batch
        
        df.at[j,"lead_time_test"] = environment.get_env().job.lead_time/2
        df.at[j, "done"] = environment.get_env().number_echu == 0
        df.at[j, "rewards"] = reward_batch
        
        planning = environment.get_env().get_gant_formated()
        planning_tot  = pd.concat([planning_tot,planning])
    
        
    historic_time_tot = (futur_state.index.to_series()).tolist()
    historic_operator_tot = futur_state["operator"].tolist()
    
    utils.visualize(planning_tot,historic_time_tot,historic_operator_tot)
        
    df["delta_lead_time"] = df["lead-time broyage->remplissage"] - df["lead_time_test"]
    df_done = df[df["done"] == True]
    
    nbr_done = len(df_done)
    completion_rate = len(df_done)/len(df)
    min_delta = df_done["delta_lead_time"].min()
    max_delta = df_done["delta_lead_time"].max()
    mean_delta = df_done["delta_lead_time"].mean()
    std_delta = df_done["delta_lead_time"].std()
    sum_delta = df_done["delta_lead_time"].sum()
    
    print("number done : ", nbr_done)
    print("completion_rate : ", completion_rate)
    print("min_delta : ", min_delta)
    print("max_delta : ", max_delta)
    print("mean_delta : ", mean_delta)
    print("std_delta : ", std_delta)
    print("sum_delta : ", sum_delta)
    
    df.to_csv("test_model.csv", sep = ";", columns = df.columns, header = True)




def evaluate_model(agent, environment, operator_vector_length, echu_weights):
    #LOAD THE TEST FILE
    df = pd.read_excel("data/test_set.xlsx")
    
    formulations = np.array(df["FORMULATION"].tolist())
    targets = np.array(df["DATE DEBUT REMPLISSAGE"].tolist())
    lead_times = np.array(df["lead-time broyage->remplissage"].tolist())
    echelles = np.array(df["ECHELLE"].tolist())
    job_names = np.array(df["CODE TRANSIT."].tolist())
    
    formulations = np.array(formulations)
    formulations = np.where(formulations == 3.75, 1, formulations)
    formulations = np.where(formulations == 11.25, 3, formulations)
    formulations = np.where(formulations == 22.5, 6, formulations)
    formulations = formulations.astype(int)
    
    df["lead_time_test"] = 0
    df["done"] = False
    df["rewards"] = -100
    
    nbr_job_to_use = len(targets)
    
    
    
    reward_tot = 0
    futur_state = None
    planning_tot = None
    for j in range(nbr_job_to_use):
        # Initialize episode
        target = targets[j]
        formulation = formulations[j]
        echelle = echelles[j]
        job_name = job_names[j]
        
        environment.job_name = job_name
        environment.target = target
        environment.formulation = formulation
        environment.echelle = echelle
        environment.futur_state = futur_state
        states = environment.reset()
        reward_batch = 0
        terminal = False
        internals = agent.initial_internals()
        
        while not terminal:
             # Episode timestep
            actions, internals = agent.act(states=states, internals = internals, independent=True)
            states, terminal, reward = environment.execute(actions=actions)
    
            reward_batch += reward
            
        futur_state = environment.get_env().state_full
        reward_tot += reward_batch
        
        df.at[j,"lead_time_test"] = environment.get_env().job.lead_time/2
        df.at[j, "done"] = environment.get_env().number_echu == 0
        df.at[j, "rewards"] = reward_batch
        
        planning = environment.get_env().get_gant_formated()
        planning_tot  = pd.concat([planning_tot,planning])
    
        
    historic_time_tot = (futur_state.index.to_series()).tolist()
    historic_operator_tot = futur_state["operator"].tolist()
    
    #utils.visualize(planning_tot,historic_time_tot,historic_operator_tot)
        
    
    df["delta_lead_time"] = df["lead-time broyage->remplissage"] - df["lead_time_test"]
    df_done = df[df["done"] == True]
    
    nbr_done = len(df_done)
    completion_rate = len(df_done)/len(df)
    min_delta = df_done["delta_lead_time"].min()
    max_delta = df_done["delta_lead_time"].max()
    mean_delta = df_done["delta_lead_time"].mean()
    std_delta = df_done["delta_lead_time"].std()
    sum_delta = df_done["delta_lead_time"].sum()
    
    df.to_csv("test_model.csv", sep = ";", columns = df.columns, header = True)
    
    return nbr_done, completion_rate, min_delta, max_delta, mean_delta, std_delta, sum_delta, reward_tot





