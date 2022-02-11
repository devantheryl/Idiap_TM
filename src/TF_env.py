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
from src.Production_line2 import Production_line
import src.utils as utils
import time

class TF_environment(Environment):
    
    def __init__(self):
        
        super().__init__()
        self.production_line = Production_line()
        self.max_step_per_episode = 500
        
        
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
        self.production_line = Production_line()
        action_mask = self.production_line.get_mask()
        
        # Add action mask to states dictionary (mask item is "[NAME]_mask", here "action_mask")
        states = dict(state = self.production_line.get_state(),  action_mask = action_mask)
        
        return states
    
    def execute(self,actions):
        # Compute terminal and reward
        next_state,reward, done  = self.production_line.step(actions)
        action_mask =self.production_line.get_mask()

        # Add action mask to states dictionary (mask item is "[NAME]_mask", here "action_mask")
        states = dict(state=next_state, action_mask=action_mask)

        return states, done, reward
    
    def get_env(self):
        return self.production_line
    
    
    