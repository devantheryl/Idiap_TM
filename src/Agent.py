from src.Job import Job
from src.Production_line import Production_line
from src.Machine import Machine
import numpy as np
import random 

class Agent:
        
        def __init__(self,prod_line):
            
            self.time = 0
            self.planning = []
            self.prod_line = prod_line
            
    
            
        def get_available_operation(self):
            
            plateau_operation = self.prod_line.get_plateau_operation()
            operation_available = []
            nbr_job = plateau_operation.shape[0]
            nbr_operation = plateau_operation.shape[1]
            
            for job in range(nbr_job):
                for operation in range(nbr_operation):
                    the_operation = plateau_operation[job,operation]
                    
                    if  the_operation != None:
                        #executable et pas assigné
                        if the_operation.get_executable() and the_operation.get_status() == 0 :
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
            self.prod_line.execute_action(decision)
            return decision
            
        def get_planning(self):
            
            return self.planning
        
        def get_prod_line(self):
            return self.prod_line
            
        
        