# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 10:29:00 2021

@author: LDE
"""

from src.Job2 import Job
from src.Machine2 import Machine

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta, date

#to set the current working directory
os.chdir("C:/Users/LDE/Prog/projet_master/digital_twins")

class Production_line():
    
    def __init__(self,time = datetime.fromisoformat('2022-01-01 00:00:00')):
        
        with open("src/config.json") as json_file:
            config = json.load(json_file)
        self.nbr_job_max = config["nbr_job_max"]
        self.nbr_operations = config["nbr_operation_max"]
        self.nbr_machines = config["nbr_machines"]
        self.nbr_operator = config["nbr_operator"]
        
        self.job_launched = False
        self.init_time = time
        self.time = time
        self.target_date = config["target_date"]
        
        
        #params
        self.wip = 0
        
        #list to keep the jobs objects
        self.jobs = np.full(self.nbr_job_max,None)
        
        #list to keep the machines objects
        self.machines = self.create_machines()
        
        #all the actions we can take
        self.actions_space = self.create_actions_space()
        
        #state size
        self.state_size = self.get_state_size()
        
        self.reset()
        
        
    def reset(self):
        
        for i in range(self.nbr_job_max):
            job = Job("TEST" + str(i), 1,20000, self.nbr_operations, datetime.fromisoformat(self.target_date[i]))
            self.add_job(job)
            
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
        action = self.actions_space[action_index]
        reward = 0
        
        #si l'action est légal, normalement elle l'est du au mask
        if self.check_legality(action):
            job_to_schedule = action[0]
            operation_to_schedule = action[1]
            machine_to_schedule = action[2]
            
            
            if action == "forward":
                if self.time.time().hour == 00:
                    self.time += timedelta(hours = 12)
                else:
                    self.time += timedelta(days=1)
                    self.time = self.time.replace(hour = 00)
                
                reward -= self.wip #a tester, on augmente la pénalitém d'avancer dans le temps en fonction du nombre de wip
                
                #update the processing time of all operation and remove the op from
                #machine if the op has ended
                #on libère aussi les opérateurs
                self.update_processing_time()
                
                #incremente lead_time for all job
                for job in self.jobs:
                    if job != None:
                        job.increment_lead_time()
                    
                #update and check expiration time of all operations
                if self.update_check_expiration_time():
                    reward -=1 # a tester, pour éviter les doublons
                
                #update and check newly executable operations
                self.update_check_executable()
                    
            
            else:
                self.job_launched = True
                #le job est lancé au broyage polymère
                if operation_to_schedule == 1:
                    self.jobs[job_to_schedule-1].started = True
                    self.wip +=1
                
                #le job se fini au retour IRR
                if operation_to_schedule == 14:
                    self.jobs[job_to_schedule-1].ended = True
                    self.wip -=1
                    if self.wip == 0:
                        self.job_launched = False
                
                #on set l'opération à "en cours", set the start time and the machine
                self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].status = 1
                self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].start_time = self.time
                self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].processed_on = machine_to_schedule
                
                #update the machine status
                self.machines[machine_to_schedule-1].assign_operation(job_to_schedule,operation_to_schedule)
                
                #decrease the number of operator remaining
                self.nbr_operator -= self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].operator
                
                #si l'opération est la perry
                if operation_to_schedule == 9:
                    #si on planifie pas le bon jour
                    if self.jobs[job_to_schedule-1].target_date != self.time:
                        reward-=1
                
        if (self.time-self.init_time).days > 14 and self.job_launched == False:
            reward-=1000#aussi à tester
        
        
        next_state = self.get_state()
        
        #to do, implemtner check done
        done = self.check_done()
            
                
        return next_state,reward, done 
    
    def update_processing_time(self):
        
        for job in self.jobs:
            if job != None:
                for operation in job.operations:
                    if operation != None:
                        #on vérifie que l'opération soit plannifiée
                        if operation.status == 1:
                            #si l'opration est terminée
                            if operation.forward() == 2:
                                operation.end_time = self.time
                                machine = operation.processed_on
                                self.machines[machine-1].remove_operation()
                                
                                self.nbr_operator += operation.operator
                                
    def update_check_executable(self):
        for job in self.jobs:
            if job != None:
                for operation in job.operations:
                    if operation != None:
                        if operation.status == 0 and operation.executable == False:
                            executable = True
                            for dependencie in operation.dependencies:
                                #si l'opération précédente est terminée
                                if job.operations[dependencie-1].status != 2:
                                    executable = False
                            if executable:
                                operation.executable = executable
                        
                        
    def update_check_expiration_time(self):
        
        for job in self.jobs:
            if job != None:  
                for operation in job.operations:
                    if operation != None:    
                        #si l'opération est terminée
                        if operation.status == 2:
                            #si l'opération suivante n'a pas encore commencé
                            if job.operations[operation.used_by-1].status == 0:
                            
                                #si l'opération est écheue
                                if operation.decrease_get_expiration_time() == 0:
                                    #l'opération suivante n'est plus executable
                                    job.operations[operation.used_by-1].executable = False
                                    #on recréer une operation
                                    job.create_operation(operation.operation_number)
                                    
                                    return True
        return False
                                
    def check_done(self):
        
        done = True
        for job in self.jobs:
            if job != None:  
                for operation in job.operations:
                    if operation != None:    
                        if not (operation.status == 2 or operation.status == 3):
                            done = False
        return done
                                
        
    
    def check_legality(self,action):
        
        if action == "forward":
            return 1
        job_to_schedule = int(action[0])
        operation_to_schedule = int(action[1])
        machine_to_schedule = int(action[2])
        
        job = self.jobs[job_to_schedule-1]
        if job != None:
            operation = job.operations[operation_to_schedule-1]
            if operation != None:
                if operation.status == 0 and operation.executable and operation.operator <= self.nbr_operator and self.machines[machine_to_schedule-1].status == 0:
                    return True
                
        return False
    
    def get_mask(self):
        
        mask = []
        for action in self.actions_space:
            mask.append(self.check_legality(action))    

        return mask
    
    def get_state_size(self):
        
        params_op = 4
        params_machine = 3
        state_size = self.nbr_job_max * self.nbr_operations * params_op + self.nbr_machines * params_machine + 1 + self.nbr_job_max#  +1 for the operator number + nbr_job_max for the target date
        
        return state_size
    
    def get_state(self):
        state = np.ndarray((self.state_size))
        sum_state = ()
        for job in self.jobs:
            if job != None:
                for operation in job.operations:
                    if operation != None:
                        sum_state += operation.get_state()
                    else:
                        #default state
                        sum_state += (4,0,0,0)
            else:
                for i in range (self.nbr_job_max):
                    sum_state += (4,0,0,0)

            #target date params
            sum_state += ((job.target_date - self.time).days /180,) #6 mois dans le futur max
                    
        for machine in self.machines:
            sum_state += machine.get_state()
            
        sum_state += (self.nbr_operator/12,)
        
        
        state[:] = sum_state 
        
        return state
    
    def get_gant_formated(self):
        planning = []
        for job in self.jobs:
            if job != None:
                planning.append(job.build_gant_formated())
                
        plan_df = pd.DataFrame()
        for plan in planning:
            print(plan,"\n")
            df = pd.DataFrame(plan, columns =['Job','Machine', 'Operation', 'Start','Duration','Finish'])
            plan_df = pd.concat([plan_df, df], axis=0)
        
        plan_df.reset_index(drop = True,inplace=True)
        
        plan_df['Machine']= plan_df['Machine'].astype(str)
        plan_df['Duration']= plan_df['Duration']
            
        return plan_df
        
        
    
       
   
        
    @property
    def nbr_job_max(self):
        return self.__nbr_job_max
    @nbr_job_max.setter
    def nbr_job_max(self, value):
        self.__nbr_job_max = value  
        
    @property
    def nbr_operations(self):
        return self.__nbr_operations
    @nbr_operations.setter
    def nbr_operations(self, value):
        self.__nbr_operations = value 
        
    @property
    def nbr_machines(self):
        return self.__nbr_machines
    @nbr_machines.setter
    def nbr_machines(self, value):
        self.__nbr_machines = value 
        
    @property
    def nbr_operator(self):
        return self.__nbr_operator
    @nbr_operator.setter
    def nbr_operator(self, value):
        self.__nbr_operator = value 
        
    @property
    def time(self):
        return self.__time
    @time.setter
    def time(self, value):
        self.__time = value 
        
    @property
    def jobs(self):
        return self.__jobs
    @jobs.setter
    def jobs(self, value):
        self.__jobs = value 
        
    @property
    def machines(self):
        return self.__machines
    @machines.setter
    def machines(self, value):
        self.__machines = value 
        
    @property
    def actions_space(self):
        return self.__actions_space
    @actions_space.setter
    def actions_space(self, value):
        self.__actions_space = value 
        
    @property
    def state_size(self):
        return self.__state_size
    @state_size.setter
    def state_size(self, value):
        self.__state_size = value 
        
    
                        
        