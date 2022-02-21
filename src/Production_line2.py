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
    
    def __init__(self):
        
        with open("src/config.json") as json_file:
            config = json.load(json_file)
        self.nbr_job_max = config["nbr_job_max"]
        self.nbr_operations = config["nbr_operation_max"]
        self.nbr_machines = config["nbr_machines"]
        self.nbr_operator = config["nbr_operator"]
        self.operator_vector_length = config["operator_vector_length"]
        self.operator = np.zeros((self.operator_vector_length))
        
        
        
        self.job_launched = False
        

        self.target_date = [datetime.fromisoformat(config["target_date"][i])+ timedelta(days=2) for i in range(self.nbr_job_max)]
        self.time = max(self.target_date)
        self.init_time = self.time
        self.morning_afternoon = 0 #o : morning, 1: afternoon
        
        
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
        
        self.set_operator_vector()
        self.reset()
        
        
    def reset(self):
        
        for i in range(self.nbr_job_max):
            job = Job("TEST" + str(i),i+1,1,20000, self.nbr_operations, self.target_date[i], self.time)
            self.add_job(job)
        
        self.update_check_executable()
        
        
            
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
        for key,value in batch_description["action_space_reverse"].items():
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
            
            #print(self.operator[-1])
            #print(self.time.weekday())
            
            
            if action == "forward":
                if self.time.time().hour == 12:
                    self.time -= timedelta(hours = 12)
                    self.morning_afternoon = 0
                else:
                    self.time -= timedelta(days=1)
                    self.time = self.time.replace(hour = 12)
                    self.morning_afternoon = 1
                
                #update the operator
                self.update_operator_vector()
                update = self.operator
                time = self.time
                
                reward -= self.wip #a tester, on augmente la pénalité d'avancer dans le temps en fonction du nombre de wip
                if reward == 0:
                    reward-=1
                
                
                #update the processing time of all operation and remove the op from
                #machine if the op has ended
                #on libère aussi les opérateurs
                ended_operations = self.update_processing_time()
                for op in ended_operations :
                    if op == 1:
                        self.wip-=1
                
                #incremente lead_time for all job
                for job in self.jobs:
                    if job != None:
                        if job.started == True:
                            job.increment_lead_time()
                    
                #update and check expiration time of all operations
                nbr_echu = self.update_check_expiration_time()
                reward -= nbr_echu*10 # a tester, pour éviter les doublons
                
                #update and check newly executable operations
                executables = self.update_check_executable()
                
                if abs(self.time-self.init_time).days > 7 and self.job_launched == False:
                    reward-=1000#aussi à tester
            
            else:
                self.job_launched = True
                #le job est lancé au broyage polymère
                if (operation_to_schedule == 9) and self.jobs[job_to_schedule-1].started ==False:
                    self.jobs[job_to_schedule-1].started = True
                    self.wip +=1
                
                #le job se fini au retour IRR
                if operation_to_schedule == 1:
                    self.jobs[job_to_schedule-1].ended = True
                    if self.wip == 0:
                        self.job_launched = False
                        self.init_time = self.time
                
                reward -= 1
                
                #on set l'opération à "en cours", set the start time and the machine
                self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].status = 1
                self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].start_time = self.time
                self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].processed_on = machine_to_schedule
                
                #update the machine status
                self.machines[machine_to_schedule-1].assign_operation(job_to_schedule,operation_to_schedule)
                
                #decrease the number of operator remaining
                op_duration = self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].processing_time
                
                self.operator[0:op_duration] -= self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].operator
                
                
                
        
        
        next_state = self.get_state()
        
        #to do, implemtner check done
        done = self.check_done()
            
                
        return next_state,reward/10, done 
    
    def update_processing_time(self):
        
        ended_operations = []
        for job in self.jobs:
            if job != None:
                for operation in job.operations:
                    if operation != None:
                        #on vérifie que l'opération soit plannifiée
                        if operation.status == 1:
                            #si l'opration est terminée
                            if operation.forward() == 2:
                                operation.end_time = self.time
                                ended_operations.append(operation.operation_number)
                                machine = operation.processed_on
                                self.machines[machine-1].remove_operation()
                                
                                #self.operator += operation.operator
                                
                                
                                
        return ended_operations
                                
    def update_check_executable(self):
        executables = []
        for job in self.jobs:
            if job != None:
                for operation in job.operations:
                    if operation != None:
                        if operation.status == 0 and operation.executable == False:
                            executable = True
                            for dependencie in operation.dependencies:
                                #si l'opération précédente n'est pas terminée
                                if job.operations[dependencie-1].status != 2:
                                    executable = False
                            
                            if operation.begin_day == 1 and self.morning_afternoon == 1:
                                executable = False
                            
                            duration = operation.processing_time
                            for i in range(duration):
                                if self.operator[i] <= 0:
                                    executable = False
                            
                            if operation.op_type == "liberation" and executable == True:
                                self.jobs[job.job_number-1].operations[operation.operation_number-1].status = 1
                                self.jobs[job.job_number-1].operations[operation.operation_number-1].start_time = self.time
                                self.jobs[job.job_number-1].operations[operation.operation_number-1].processed_on = 0
                                
                            if operation.operation_number == 9:
                                if self.time > job.target_date:
                                    executable = False
                            
                            if executable:
                                executables.append(operation.operation_number)
                            operation.executable = executable
                        #si op = perry
                        
        return executables
                        
    def update_check_expiration_time(self):
        
        nbr_echu = 0
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
                                    
                                    nbr_echu += 1
        return nbr_echu
                                
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
                if operation.status == 0 and operation.executable and operation.operator <= self.operator[0] and self.machines[machine_to_schedule-1].status == 0:
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
        state_size = self.nbr_job_max * self.nbr_operations * params_op + self.nbr_machines * params_machine + self.operator_vector_length + 1#  +1 for morning afternoon
        
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

                    
        for machine in self.machines:
            sum_state += machine.get_state()
            
        sum_state += tuple(self.operator/12)
        
        sum_state += (self.morning_afternoon,)
        
        
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
        
    def set_operator_vector(self):
        current_date = self.time
        
        for i in range(int(self.operator_vector_length)):
            #si jour de weekend
            if current_date.weekday() > 4:
                self.operator[i] = 0
            #TODO ajouter les jours férier + vacances
            else:
                self.operator[i] = self.nbr_operator
                
            if current_date.hour == 12:
                current_date -= timedelta(hours = 12)
            else:
                current_date -= timedelta(days=1)
                current_date = current_date.replace(hour = 12)
    
    def update_operator_vector(self):
        
        self.operator = np.roll(self.operator,-1)
        new_date = self.time - timedelta(days= self.operator_vector_length/2)
        if new_date.weekday() > 4:
            self.operator[-1] = 0
        #TODO ajouter les jours férier + vacances
        else:
            self.operator[-1] = self.nbr_operator
        
            
                
        
    
       
   
        
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
        
    
                        
        