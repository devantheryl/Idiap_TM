# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 10:29:00 2021

@author: LDE
"""

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
            
    
    
    def step(action):
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
        return None
    
    
       
   
        
        
        