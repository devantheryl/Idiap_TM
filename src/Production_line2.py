# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 10:29:00 2021

@author: LDE
"""

from src.Job2 import Job
from src.Machine2 import Machine

import numpy as np
import json
import os


#to set the current working directory
os.chdir("C:/Users/LDE/Prog/projet_master/digital_twins")

class Production_line():
    
    def __init__(self,nbr_job_max, nbr_operations,nbr_machines,nbr_operator, time):
        
        
        self.nbr_job_max = nbr_job_max
        self.nbr_operations = nbr_operations
        self.nbr_machines = nbr_machines
        self.nbr_operator = nbr_operator
        self.time = time
        
        #list to keep the jobs objects
        self.jobs = np.full(nbr_job_max,None)
        
        #list to keep the machines objects
        self.machines = self.create_machines()
        
        #all the actions we can take
        self.actions_space = self.create_actions_space()
        
    
    def create_machines(self):
        """
        create all the Machine objects

        """
        with open("src/batch_description.json") as json_file:
            batch_description = json.load(json_file)
        
        machines = np.full(self.nbr_machines, None)
        
        for i, machine_name in enumerate(batch_description["machines"]):
            machines[i] = Machine(i+1, machine_name)
            
        return machines
    
    def create_actions_space(self):
        """
        create the actions space

        """
        with open("src/batch_description.json") as json_file:
            batch_description = json.load(json_file)
            
        actions = []
        for key,value in batch_description["action_space"].items():
            for i in range(self.nbr_job_max):
                for machine in value:
                    actions.append((i+1,int(key),machine))
        actions.append("forward")
        return actions
    
    def add_job(self, job):
        """
        add a job to the prod_line's job list

        Parameters:
            job (Job): the job to add

        Returns:
            true  if done 
            false if prod_line queue is full

        """
        for i, _ in enumerate(self.jobs):
            if self.jobs[i] == None:
                self.jobs[i] = job
                return True
            
        return False
            
    
    
    def step(self, action_index):
        """
        execute an action et go 1 step-time further
        the action is a set of operation schedule on several machine
        it's possible that the action is not completely executable,
        in this case, place schedule the legal operation on the machine 
        and let the others empty

        Parameters:
            action (int): the indice of the action corresponding to 'actions_space'

        Returns:
            state (numpy.array) : the state of all operations, all machines and the #operateurs 

        """
        
        #TODO
        action = self.actions[action_index]
        
        #si l'action est légal, normalement elle l'est du au mask
        if self.check_legality(action):
            job_to_schedule = action[0]
            operation_to_schedule = action[1]
            machine_to_schedule = action[2]
            
            #to implement : state params and default state
            current_state = self.state
            reward = 0
            
            if action = "forward":
                self.time += 1
                reward = -1
                
                #updtate status, .... of all operations and machine
                for job in self.jobs:
                    for operation in job.operations:
                        
                #for op in all_op:
                    #check si l'opératon est terminée --> libérer la machine
                #increment the leadtime of all job
                #check and update the expiration time of all operation
            
            else:
                #assign l'opération, set the start time, set processed on, assign operation on the machine
                #decrease the number of operator
                
        next_state = self.state
            
            
                
        return state,action,reward,next_state
    
    def check_legality(self,actions):
        pass
        #todo
       
   
        
        
        