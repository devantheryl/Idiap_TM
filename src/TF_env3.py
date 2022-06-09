# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 11:51:35 2022

@author: LDE
"""
import json
import os
from collections import deque
import wandb
import numpy as np
from tensorforce import Environment, Runner, Agent
from src.Prod_line_3 import Production_line
import utils as utils
import time

class TF_environment(Environment):
    
    def __init__(self,target, formulation,echelle, job_name, nbr_operation_max, nbr_machines, nbr_operator, futur_length,
                 futur_state, echu_weights, forward_weights, ordo_weights, job_finished_weigths, independent =False):
        
        super().__init__()

        self.target = target
        self.formulation = formulation
        self.echelle = echelle
        self.job_name = job_name
        self.nbr_operation_max = nbr_operation_max
        self.nbr_machines = nbr_machines
        self.nbr_operator = nbr_operator
        self.futur_length = futur_length
        self.futur_state = futur_state

        self.echu_weights = echu_weights
        self.forward_weights = forward_weights
        self.ordo_weights = ordo_weights
        self.job_finished_weigths = job_finished_weigths
        self.independent = independent
        self.production_line = Production_line(self.target, self.formulation,self.echelle, self.job_name, self.nbr_operation_max, self.nbr_machines,
                                               self.nbr_operator,self.futur_length, self.futur_state,  self.echu_weights, self.forward_weights,
                                               self.ordo_weights, self.job_finished_weigths)
        self.max_step_per_episode = 100
        self.i = 0
        self.nbr_echu =0
        
        
    def states(self):
        
        return dict(type="float", shape=(self.production_line.state_size))
    
    def actions(self):
        return dict(type="int", num_values = len(self.production_line.actions_space))
    
    def max_episode_timesteps(self):
        return self.max_step_per_episode
    
    def close(self):
        super().close()
        
    def reset(self):
        
            
        # Initial state and associated action mask
        self.production_line = Production_line(self.target, self.formulation,self.echelle, self.job_name, self.nbr_operation_max, self.nbr_machines,
                                               self.nbr_operator,self.futur_length, self.futur_state,  self.echu_weights, self.forward_weights,
                                               self.ordo_weights, self.job_finished_weigths)
        
        action_mask = self.production_line.get_mask()
        
        # Add action mask to states dictionary (mask item is "[NAME]_mask", here "action_mask")
        states = dict(state = self.production_line.get_state(),  action_mask = action_mask)
        
        return states
    
    def execute(self,actions):
        # Compute terminal and reward
        next_state,reward, done, self.nbr_echu  = self.production_line.step(actions)
        action_mask =self.production_line.get_mask()

        # Add action mask to states dictionary (mask item is "[NAME]_mask", here "action_mask")
        states = dict(state=next_state, action_mask=action_mask)

        return states, done, reward
    
    def get_env(self):
        return self.production_line
    
    
    