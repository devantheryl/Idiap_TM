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
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        
        #experience replay
        self.memory = deque(maxlen = 20000)
        
        #discount rate
        self.gamma = 0.95
        
        #epsilon-greedy params
        self.epsilon = 1.0
        self.epsilon_decay = 0.99995
        self.epsilon_min = 0.01
        
        self.learning_rate = 0.0001
        
        self.model = self._build_model()
        self.target = self._build_model()
        self.alighn_target_model()
    
    def set_test_mode(self,value,gamma = 0.95):
    
        if value:
            self.gamma = 0
        else:
            self.gamma = gamma
            
    
    def _build_model(self):
          
        model = Sequential()
        
        #hyper params to tune
        model.add(Dense(240, input_dim = self.state_size, activation = 'relu'))
        model.add(Dense(480, activation = 'relu'))
        model.add(Dense(self.action_size, activation = 'linear'))
        
        model.compile(loss = 'huber_loss', optimizer = Adam(learning_rate = self.learning_rate))
        
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
                
                
        self.model.fit(states, pred_Q, epochs =1, verbose = 0)        
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        
    def load(self, path):
        self.model.load_weights(path)
        
    def save(self, path):
        self.model.save_weights(path)