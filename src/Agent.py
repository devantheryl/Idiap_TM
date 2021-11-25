from src.Job import Job
from src.Production_line import Production_line
from src.Machine import Machine
import numpy as np
import random 
import pandas as pd
from datetime import datetime

from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Dense, Embedding, Reshape
from tensorflow.keras.optimizers import Adam

max_jobs = 14
nbr_operations = 14
nbr_machine = 14
nbr_operateur = 12 #changer pour avoir un nombre dynamique

class Agent:
        
        def __init__(self,prod_line,optimizer):
            
            self.time = 0
            self.prod_line = prod_line
            self.reward = 0
            
            self.action_space_size = len(prod_line.get_action_space())
            #job state * 4 params, machine state * 3 params + operateur_dispo
            self.state_space_size = prod_line.get_plateau_operation().size * 4 + prod_line.get_plateau_machine().size * 3 + 1
            
            self.database = self.init_database()
            
            #RL
            self.optimizer = optimizer
            self.gamma = 0.6
            self.epsilon = 0.1
            
            #build the two NN
            self.q_network = self._build_compile_model()
            self.target_network = self._build_compile_model()
            self.copy_to_target_model()
            
            
        def _build_compile_model(self):
            model = Sequential()
            model.add(Embedding(self.state_space_size, 10, input_length=1))
            model.add(Reshape((10,)))
            model.add(Dense(50, activation='relu'))
            model.add(Dense(50, activation='relu'))
            model.add(Dense(self.action_space_size, activation='linear'))
            
            model.compile(loss='mse', optimizer=self.optimizer)
            return model
        
        def copy_to_target_model(self):
            self.target_network.set_weights(self.q_network.get_weights())
            
        def retrain(self, batch_size):
            batch = np.random.choice(self.database, batch_size)
            
            for state, action, reward, next_state, terminated in batch:
                
                target = self.q_network.predict(state)
                
                if terminated:
                    target[0][action] = reward
                else:
                    t = self.target_network.predict(next_state)
                    target[0][action] = reward + self.gamma * np.amax(t)
                
                self.q_network.fit(state, target, epochs=1, verbose=0)
        
        
        def init_database(self):
            database_size = self.state_space_size *2 + 2
            return np.empty((0,database_size))
        
        def write_db(self,path):
            np.savetxt(path, self.database,delimiter=';',fmt='%5s')
            
            
        def get_available_operation(self):
            
            operateur_available = self.prod_line.get_operateur_available()
            plateau_operation = self.prod_line.get_plateau_operation()
            operation_available = []
            nbr_job = plateau_operation.shape[0]
            nbr_operation = plateau_operation.shape[1]
            
            for job in range(nbr_job):
                for operation in range(nbr_operation):
                    the_operation = plateau_operation[job,operation]
                    
                    if  the_operation != None:
                        #executable et pas assigné
                        operateur_needed = the_operation.get_operator()
                        if the_operation.get_executable() and the_operation.get_status() == 0 and operateur_needed <= operateur_available:
                            operation_available.append((job+1,operation+1))
                            
            return operation_available
                            
        def get_available_actions(self):
            
            operation_available = self.get_available_operation()    
            available_actions = []
            action_space = self.prod_line.get_action_space()
            plateau_machine = self.prod_line.get_plateau_machine()
            for action in action_space:
                for operation in operation_available:
                    if action[0] == operation[0] and action[1] == operation[1] and plateau_machine[action[2]-1].get_status() ==0:
                        available_actions.append(action)
            available_actions.append("forward")
            
            return available_actions
        
        
        
        def take_decision(self):
            
            if np.random.rand() <= self.epsilon:
                actions = self.get_available_actions()
                decision = random.choice(actions)
            
            else:
                state_dict = self.prod_line.get_rl_formated_state("")
                
                #to add : the prediction of NN fiven the current_state
                
                actions = self.get_available_actions()#temp
                decision = random.choice(actions)#temp
            
            current_state,action,reward,next_state = self.prod_line.execute_action(decision)
            
            
            self.add_to_db(current_state,action,reward,next_state)
            return current_state,action,reward,next_state

        
        def get_prod_line(self):
            return self.prod_line
            
        def add_to_db(self,current_state,action,reward,next_state):
            self.database = np.append(self.database,(current_state,action,reward,next_state))
            
        def get_db(self):
            return self.database