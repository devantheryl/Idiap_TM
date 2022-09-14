# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 11:51:35 2022

@author: LDE
"""
import json
import os
from collections import deque
import numpy as np
from tensorforce import Environment, Runner, Agent
from src.Prod_line_3 import Production_line

import time

class TF_environment(Environment):
    
    def __init__(self,nbr_operation_max, nbr_machines, futur_length,
                 echu_weights, forward_weights, ordo_weights, job_finished_weigths, independent =False):
        
        super().__init__()

        """
        variables for the state_space
        """
        self.nbr_operation_max = nbr_operation_max
        self.nbr_machines = nbr_machines
        self.futur_length = futur_length

        """
        variables for the RL reward
        """
        self.echu_weights = echu_weights
        self.forward_weights = forward_weights
        self.ordo_weights = ordo_weights
        self.job_finished_weigths = job_finished_weigths
        
        self.independent = independent
        
        self.production_line = Production_line(self.nbr_operation_max, self.nbr_machines, self.futur_length, 
                                               self.echu_weights, self.forward_weights, self.ordo_weights, self.job_finished_weigths)
        self.max_step_per_episode = 200
        
        
    def states(self):
        
        return dict(type="float", shape=(self.production_line.state_size))
    
    def actions(self):
        return dict(type="int", num_values = len(self.production_line.actions_space))
    
    def max_episode_timesteps(self):
        return self.max_step_per_episode
    
    def close(self):
        super().close()
        
    def reset(self):
        
        
        self.production_line.reset()
        
        action_mask = self.production_line.get_mask()
        
        # Add action mask to states dictionary (mask item is "[NAME]_mask", here "action_mask")
        states = dict(state = self.production_line.get_state(),  action_mask = action_mask)
        
        return states
    
    def execute(self,actions):
        # Compute terminal and reward
        next_state,reward, done, nbr_echu  = self.production_line.step(actions)
        action_mask =self.production_line.get_mask()

        # Add action mask to states dictionary (mask item is "[NAME]_mask", here "action_mask")
        states = dict(state=next_state, action_mask=action_mask)

        return states, done, reward
    
    def get_env(self):
        return self.production_line
    
    
    