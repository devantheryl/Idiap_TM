from src.Job import Job
from src.Production_line import Production_line
from src.Machine import Machine
import numpy as np
import random 
import pandas as pd
from datetime import datetime

max_jobs = 4
nbr_operations = 14
nbr_machine = 14
nbr_operateur = 12 #changer pour avoir un nombre dynamique

class Agent:
        
        def __init__(self,prod_line):
            
            self.time = 0
            self.prod_line = prod_line
            self.reward = 0
            self.database = self.init_database()
            
            
        def init_database(self):
            columns = []
            for job in range(max_jobs):
                for operation in range(nbr_operations):
                    job_number = job+1
                    operation_number = operation+1
                    
                    columns.append("current" + "_" + "status" + "_" + str(job_number) + "_" + str(operation_number))
                    columns.append("current" + "_" + "processing_time" + "_"  + str(job_number) + "_" + str(operation_number))
                    columns.append("current" + "_" + "nbr_of_sucessor" + "_"  + str(job_number) + "_" + str(operation_number))
                    columns.append("current" + "_" + "expiration_time" + "_"  + str(job_number) + "_" + str(operation_number))
                    columns.append("current" + "_" + "remaining_time" + "_"  + str(job_number) + "_" + str(operation_number))
                    columns.append("current" + "_" + "executable" + "_"  + str(job_number) + "_" + str(operation_number))
                    
            for i,machine in enumerate(self.prod_line.get_plateau_machine()):
                columns.append("current" + "_" + "status" + "_" + str(i+1))
                columns.append("current" + "_" + "job" + "_" + str(i+1))
                columns.append("current" + "_" + "operation" + "_" + str(i+1))

            columns.append("current" + "_" + "operateur_dispo")  
            
            columns.append("action")
            columns.append("reward")
            
            for job in range(max_jobs):
                for operation in range(nbr_operations):
                    job_number = job+1
                    operation_number = operation+1
                    
                    columns.append("next" + "_" + "status" + "_" + str(job_number) + "_" + str(operation_number))
                    columns.append("next" + "_" + "processing_time" + "_"  + str(job_number) + "_" + str(operation_number))
                    columns.append("next" + "_" + "nbr_of_sucessor" + "_"  + str(job_number) + "_" + str(operation_number))
                    columns.append("next" + "_" + "expiration_time" + "_"  + str(job_number) + "_" + str(operation_number))
                    columns.append("next" + "_" + "remaining_time" + "_"  + str(job_number) + "_" + str(operation_number))
                    columns.append("next" + "_" + "executable" + "_"  + str(job_number) + "_" + str(operation_number))
                    
            for i,machine in enumerate(self.prod_line.get_plateau_machine()):
                columns.append("next" + "_" + "status" + "_" + str(i+1))
                columns.append("next" + "_" + "job" + "_" + str(i+1))
                columns.append("next" + "_" + "operation" + "_" + str(i+1))

            columns.append("next" + "_" + "operateur_dispo")  
            

            return pd.DataFrame(data = None, columns = columns)     
        
        def write_db(self,path):
            self.database.to_csv(path, sep = ';')
            
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
        
            actions = self.get_available_actions()
            decision = random.choice(actions)
            current_state,action,reward,next_state = self.prod_line.execute_action(decision)
            globale_state ={}
            globale_state.update(current_state)
            globale_state.update({"action" : action})
            globale_state.update({"reward" : reward})
            globale_state.update(next_state)
            
            self.add_to_db(globale_state)
            return current_state,action,reward,next_state

        
        def get_prod_line(self):
            return self.prod_line
            
        def add_to_db(self,globale_state):
            self.database = self.database.append(globale_state,ignore_index = True)
            
        def get_db(self):
            return self.database