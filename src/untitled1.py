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
import src.utils as utils
from random import sample

#to set the current working directory
os.chdir("C:/Users/LDE/Prog/projet_master/digital_twins")

class Production_line():
    
    def __init__(self,target, nbr_operation_max, nbr_machines, nbr_operator, futur_length,
                 futur_machine, futur_operator, echu_weights, no_target_weights):
        
        

        self.nbr_operation_max = nbr_operation_max
        self.nbr_machines = nbr_machines
        self.nbr_operator = nbr_operator
        
        self.futur_operator = futur_operator
        self.futur_machine = futur_machine
        
        
        self.historic_operator = []
        self.historic_time = []
        self.job_launched = False
        

        self.target_date = []
        self.formulations = []
        
        self.echu_weights = echu_weights
        self.no_target_weights = no_target_weights
        
        
        for i, (key, value) in enumerate(dict_target_date.items()):
            if i < self.nbr_job_to_use:
                self.target_date.append(datetime.fromisoformat(key) + timedelta(days = 2))
                self.formulations.append(value)
            
                
        self.time = max(self.target_date)
        self.init_time = self.time 
        self.morning_afternoon = 0 #0: morning, 1: afternoon
        
        
        self.number_echu = 0
        self.number_no_target = 0
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
        
        for i in range(len(self.target_date)):
            job = Job("TEST" + str(i),i+1,self.formulations[i],20000, self.nbr_operation_max, self.target_date[i], self.time)
            self.add_job(job)
        
        
        #TOTEST, PLAN PERRY WTHOUT THE AGENT 
        for i, job in enumerate(self.jobs):
            #jour de perry, on la planifie d'office
            if job != None:
                if job.target_date == self.time:
                    self.jobs[i].started = True
                    self.jobs[i].operations[15-1].status = 1
                    self.jobs[i].operations[15-1].end_time = self.time
                    self.jobs[i].operations[15-1].processed_on = 8
                    self.wip +=1
                    #update the machine status
                    self.machines[8-1].assign_operation(i+1,15)
        
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
        available_index = []
        
        #get available index in the job grid
        for i, _ in enumerate(self.jobs):
            if self.jobs[i] == None:
                available_index.append(i)
                
        #assign the job to a random available place in the grid
        if len(available_index):
            i = sample(available_index,1)[0]
            job.job_number = i+1
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
        nbr_echu = 0
        test = self.check_legality(action)
        if test == False:
            print("problem")
        #si l'action est légal, normalement elle l'est du au mask
        if self.check_legality(action):
            job_to_schedule = action[0]
            operation_to_schedule = action[1]
            machine_to_schedule = action[2]
            
            #print(self.operator[-1])
            #print(self.time.weekday())
            
            
            if action == "forward":
                
                
                self.historic_operator.append(self.operator[0])
                
                if self.time.time().hour == 12:
                    self.time -= timedelta(hours = 12)
                    self.morning_afternoon = 0
                else:
                    self.time -= timedelta(days=1)
                    self.time = self.time.replace(hour = 12)
                    self.morning_afternoon = 1
                    
                self.historic_time.append(self.time)
                
                #update the operator
                self.update_operator_vector()
                update = self.operator
                time = self.time
                
                reward -= self.wip #a tester, on augmente la pénalité d'avancer dans le temps en fonction du nombre de wip
                
                if reward == 0:
                    reward-=1
                
                
                #incremente lead_time for all job
                for job in self.jobs:
                    if job != None:
                        if job.started == True:
                            job.increment_lead_time()
                    
                #update and check expiration time of all operations
                nbr_echu, job_ended = self.update_check_expiration_time()
                self.number_echu += nbr_echu
                reward -= self.echu_weights*nbr_echu # a tester, pour éviter les doublons
                
                for job in job_ended:
                    
                    self.jobs[job-1].remove_all_operation()
                    self.jobs[job-1].ended = True
                    self.wip -=1
                #update the processing time of all operation and remove the op from
                #machine if the op has ended
                #on libère aussi les opérateurs
                ended_operations = self.update_processing_time()
                
                        
                
                #TOTEST, PLAN PERRY WTHOUT THE AGENT 
                for i, job in enumerate(self.jobs):
                    if job != None:
                        #jour de perry, on la planifie d'office
                        if job.target_date == self.time:
                            self.jobs[i].started = True
                            self.jobs[i].operations[15-1].status = 1
                            self.jobs[i].operations[15-1].end_time = self.time
                            self.jobs[i].operations[15-1].processed_on = 8
                            self.wip+=1
                            #update the machine status
                            self.machines[8-1].assign_operation(i+1,15)
                            
            
            else:
                self.job_launched = True
                #le job est lancé au broyage polymère
                if (operation_to_schedule == 15) and self.jobs[job_to_schedule-1].started ==False:
                    self.jobs[job_to_schedule-1].started = True
                    self.wip +=1 
                
                reward += 1
                
                #on set l'opération à "en cours", set the start time and the machine
                self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].status = 1
                self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].end_time = self.time
                self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].processed_on = machine_to_schedule
                
                
                #update the machine status
                self.machines[machine_to_schedule-1].assign_operation(job_to_schedule,operation_to_schedule)
                
                #decrease the number of operator remaining
                op_duration = self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].processing_time
                
                self.operator[0:op_duration] -= self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].operator
                
                
                #si l'opération est la perry
                if self.jobs[job_to_schedule-1].operations[operation_to_schedule-1].operation_number == 15:
                    if self.jobs[job_to_schedule-1].target_date != self.time:
                        reward-= self.no_target_weights + abs(utils.get_delta_time(self.time, self.jobs[job_to_schedule-1].target_date))
                        self.number_no_target +=1

                
                
                
        #update and check newly executable operations
        executables = self.update_check_executable()
        
        next_state = self.get_state()
        
        done, jobs_done  = self.check_done()
    
        
        if jobs_done != None:
            self.jobs[jobs_done-1].remove_all_operation()
            self.jobs[jobs_done-1].ended = True
            self.wip -=1
            reward += 40
        if done:
            print("done")
            #reward += 10
            
        #if self.number_echu >0:
            #done = True
                  
                
        return next_state,reward, done, nbr_echu
    
    def update_processing_time(self):
        
        ended_operations = []
        for job in self.jobs:
            if job != None:
                for operation in job.operations:
                    if operation != None:
                        #on vérifie que l'opération soit plannifiée
                        if operation.status == 1:
                            #si l'opration est terminée
                            if operation.forward() == -1:
                                operation.start_time = self.time
                                ended_operations.append(operation.operation_number)
                                machine = operation.processed_on
                                self.machines[machine-1].remove_operation()
                                
                                #self.operator += operation.operator
                                
                                
                                
        return ended_operations
           
    def update_check_expiration_time(self):
        
        nbr_echu = 0
        job_ended = []
        for job in self.jobs:
            if job != None:  
                for operation in job.operations:
                    if operation != None:    
                        #si l'opération est terminée
                        if operation.status == -1:
                                          
                            for operation_used in operation.used_by:
                                #si l'opérations suivantes n'a pas encore commencé
                                if job.operations[operation_used-1].status == 0:
                            
                                    #si l'opération est échue
                                    if job.operations[operation_used-1].decrease_get_expiration_time(self.time) == 0:

                                        job_ended.append(job.job_number)
                                        
    
                                        nbr_echu += 1
                                        job.echu += [operation_used]
                                        
                                        break           
                                        
        return nbr_echu, job_ended
    
                     
    def update_check_executable(self):
        executables = []
        for job in self.jobs:
            if job != None:
                for operation in job.operations:
                    if operation != None:
                        if operation.status == 0: #and operation.executable == False:
                            executable = True
                            for dependencie in operation.dependencies:
                                #si l'opération précédente n'est pas terminée
                                if job.operations[dependencie-1].status != -1:
                                    executable = False
                            
                            
                            duration = operation.processing_time
                            
                            #L'opération doit commencer le matin
                            if operation.begin_day == 1:
                                begin_time = utils.get_new_time(self.time, -duration)
                                if begin_time.time().hour == 12:
                                    executable = False
                                
                            if operation.QC_delay >0:
                                executable = False
                            
                            
                            for i in range(duration):
                                if self.operator[i] < operation.operator:
                                    executable = False
                            
                            
                            #TODO change the static rule
                            if operation.operation_number == 15:
                                if self.time > job.target_date:
                                    executable = False
                                
                            #TODO change the static rule
                            #eviter que qu'un mélange d'un autre lot se produise pendant une extrusion
                            if operation.operation_number == 7 or operation.operation_number == 8:
                                #on check que le mélangeur soit idle
                                if self.machines[3].status != 0:
                                    executable = False
                                    
                            #TODO change this shit
                            #pour eviter que l'extrusion soit mal plannifiée (probleme de doublon)
                            if operation.operation_number == 8 or operation.operation_number == 7:
                                if self.time.weekday() == 1:
                                    executable = False
                                
                            
                            if executable:
                                executables.append(operation.operation_number)
                            operation.executable = executable
                        #si op = perry
                        
        return executables
                        
    
                                
    def check_done(self):
        
        done = True
        jobs_done = None
        for job in self.jobs:
            job_done = True
            if job != None and job.ended == False:  
                for operation in job.operations:
                    if operation != None:    
                        if not (operation.status == -1):
                            done = False
                            job_done = False
                if job_done:
                    jobs_done = job.job_number
                    
                        
        return done, jobs_done
                                
        
    
    def check_legality(self,action):
        
        if action == "forward":
            return True
        job_to_schedule = int(action[0])
        operation_to_schedule = int(action[1])
        machine_to_schedule = int(action[2])
        
        job = self.jobs[job_to_schedule-1]
        if job != None:
            operation = job.operations[operation_to_schedule-1]
            if operation != None:
                if operation.status == 0 and operation.executable and self.machines[machine_to_schedule-1].status == 0:
                    return True
                
        return False
    
    def get_mask(self):
        
        mask = []
        for action in self.actions_space:
            mask.append(self.check_legality(action))    

        return mask
    
    def get_state_size(self):
        
        params_op = 3
        params_machine = 1
        params_prod_line = 3
        state_size = self.nbr_job_max * self.nbr_operation_max * params_op + self.nbr_job_max + self.nbr_machines * params_machine + self.operator_vector_length + params_prod_line
        
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
                        sum_state += (0,0,0) # 1 = 4/4
                        
                #target_date delta time        
                sum_state += (utils.get_delta_time(self.time, job.target_date) /180,)
                
            else:
                for i in range (self.nbr_operation_max):
                    sum_state += (0,0,0) # 1 = 4/4
                    
                #target_date delta time  default value
                sum_state += (0,)
            
            
            
                    
        for machine in self.machines:
            sum_state += machine.get_state()
            
        sum_state += tuple((self.operator-6)/6)
        
        sum_state += (self.morning_afternoon,)
        
        sum_state += ((self.time.weekday()-3)/3,)
        
        sum_state += (self.wip/self.nbr_job_max,)
        
        state[:] = sum_state 
        
        return state
    
    def get_gant_formated(self):
        planning = []
        for job in self.jobs:
            if job != None:
                planning.append(job.build_gant_formated())
                
        plan_df = pd.DataFrame()
        for plan in planning:
            df = pd.DataFrame(plan, columns =['Job','Machine', 'Operation', 'Start','Duration','Finish'])
            plan_df = pd.concat([plan_df, df], axis=0)
        
        plan_df.reset_index(drop = True,inplace=True)
        
        plan_df['Machine']= plan_df['Machine'].astype(str)
        plan_df['Duration']= plan_df['Duration']
            
        return plan_df
    
    def get_job_stats(self):
        
        stats = {}
        #for batch
        for job in self.jobs:
            if job != None:
                stat = job.get_stats()
                stats[job.job_name] = stat
                
                
        return stats
        
        
        #TODO summarize all the stats and kpis of the prod line
        
    def set_operator_vector(self):
        current_date = self.time
        if current_date.hour == 12:
            current_date -= timedelta(hours = 12)
        else:
            current_date -= timedelta(days=1)
            current_date = current_date.replace(hour = 12)
        
        for i in range(int(self.operator_vector_length)):
            #si jour de weekend
            if current_date.weekday() > 4:
                self.operator[i] = 0
            #TODO ajouter les jours férier + vacances
            else:
                self.operator[i] = self.nbr_operator
                for target in self.target_date:
                    #perry dure 4 temps
                    for target_i in range(4):
                        perry_date = utils.get_new_time(target, -target_i-1)
                        if perry_date == current_date:
                            
                            self.operator[i] -= 8
                
                
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
            for target in self.target_date:
                #perry dure 4 temps
                for target_i in range(4):
                    perry_date = utils.get_new_time(target, -target_i-1)
                    if perry_date == new_date:
                        
                        self.operator[-1] -= 8
                        
            
                
        
    
       
   
        
    @property
    def nbr_job_max(self):
        return self.__nbr_job_max
    @nbr_job_max.setter
    def nbr_job_max(self, value):
        self.__nbr_job_max = value  
        
    @property
    def nbr_operation_max(self):
        return self.__nbr_operation_max
    @nbr_operation_max.setter
    def nbr_operation_max(self, value):
        self.__nbr_operation_max = value 
        
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
        
    
                        
        