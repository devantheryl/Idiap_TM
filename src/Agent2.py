# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 13:38:06 2021

@author: LDE
"""

import numpy as np

from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Dense, Embedding, Reshape
from tensorflow.keras.optimizers import Adam    

import time

import random 
from collections import deque

class Agent:
    def __init__(self, state_size, action_size, params_agent):
        self.state_size = state_size
        self.action_size = action_size
        
        #experience replay
        self.memory = deque(maxlen = params_agent["memory"])
        
        #discount rate
        self.gamma = params_agent["gamma"]
        
        #epsilon-greedy params
        self.epsilon_max = params_agent["epsilon"]
        self.epsilon = params_agent["epsilon"]
        self.epsilon_decay = params_agent["epsilon_decay"]
        self.epsilon_min = params_agent["epsilon_min"]
        
        self.learning_rate = params_agent["learning_rate"]
        
        self.model = self._build_model(params_agent["model"])
        self.target = self._build_model(params_agent["model"])
        self.alighn_target_model()
    
    def set_test_mode(self,value,epsilon = 1):
    
        if value:
            self.epsilon = 0
        else:
            self.epsilon = epsilon
            
    
    def _build_model(self,params):
          
        model = Sequential()
        #hyper params to tune
        model.add(Dense(params["nbr_neurone_first_layer"], input_dim = self.state_size, activation = params["activation_first_layer"]))
        model.add(Dense(params["nbr_neurone_second_layer"], activation = params["activation_second_layer"]))
        model.add(Dense(self.action_size, activation = params["output_layer_activation"]))
        
        model.compile(loss = params["loss"], optimizer = Adam(learning_rate = self.learning_rate))
        
        return model
    
    def alighn_target_model(self):
        self.target.set_weights(self.model.get_weights())
    
    def remember(self, state, action,reward,next_state,done):
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, state, mask):
        #epsilon-greedy choice of the action to perform
        if np.random.rand() <= self.epsilon:
            while True:
                action = random.randrange(self.action_size)
                if mask[action] == 1:
                    return action
            
            
        act_values = self.model.predict(state)
        act_values_masked = np.ma.masked_where(mask==0, act_values[0]) 
        return np.argmax(act_values_masked)
    
    def replay(self, batch_size):  
        
        states = np.ndarray((0,self.state_size))
        next_states = np.ndarray((0,self.state_size))
        actions = []
        rewards =[]
        terminateds = []

        minibatch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, terminated in minibatch:     
            states = np.vstack((states, state))
            next_states = np.vstack((next_states, next_state))
            actions.append(action)
            rewards.append(reward)
            terminateds.append(terminated)
        
        pred_Q = self.model.predict(states) #predicted q-values
        target_Q = self.target.predict(next_states)
        
        for i in range(len(pred_Q)):         
            if terminateds[i]:
                pred_Q[i,int(actions[i])] = rewards[i]
            else:
                pred_Q[i,int(actions[i])] = rewards[i] + self.gamma * np.amax(target_Q[i])
                
                
        history = self.model.fit(states, pred_Q, epochs =1, verbose = 0)        
        
            
        return history
        
    def update_epsilon(self,episode_number,episode_max):
        self.epsilon = self.epsilon_max - (self.epsilon_max - self.epsilon_min)/episode_max * episode_number
    
    def load(self, path):
        self.model.load_weights(path)
        
    def save(self, path):
        self.model.save_weights(path)