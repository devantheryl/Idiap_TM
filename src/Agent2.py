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
        self.memory = deque(maxlen = 2000)#check if we keep everything or not (maxlen = inf)
        
        #discount rate
        self.gamma = 0.95
        
        #epsilon-greedy params
        self.epsilon = 1.0
        self.epsilon_decay = 0.998
        self.epsilon_min = 0.005
        
        self.learning_rate = 0.001
        
        self.model = self._build_model()
    
    def _build_model(self):
        model = Sequential()
        
        #hyper params to tune
        model.add(Dense(12, input_dim = self.state_size, activation = 'relu'))
        model.add(Dense(12,activation = 'relu'))
        model.add(Dense(self.action_size, activation = 'linear'))
        
        model.compile(loss = 'mse', optimizer = Adam(lr = self.learning_rate))
        
        return model
    
    def remember(self, state, action,reward,next_state,done):
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, state):
        #epsilon-greedy choice of the action to perform
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])
    
    def replay(self, batch_size):
        
        batch = random.sample(self.memory,batch_size)
        
        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            
            self.model.fit(state, target_f, epochs =1, verbose = 0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
    def load(self, path):
        self.model.load_weights(path)
        
    def save(self, path):
        self.model.save_weights(path)