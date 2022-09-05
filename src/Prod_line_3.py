# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 10:29:00 2021

@author: LDE
"""

from src.Job2 import Job
from src.Machine2 import Machine

import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset
import json
import os
from datetime import datetime, timedelta, date
from src.batch_description import get_batch_description
from random import sample

#to set the current working directory
import sys
import os
abspath = os.path.abspath(__file__)
dname =os.path.dirname(os.path.dirname(abspath))
os.chdir(dname)

class Production_line():
    
    def __init__(self, target, formulation,echelle,job_name, nbr_operation_max, nbr_machines, nbr_operator, futur_length,
                 futur_state, echu_weights, forward_weights, ordo_weights, job_finished_weigths):
        
        
        
            
        self.nbr_operation_max = nbr_operation_max
        self.nbr_machines = nbr_machines
        self.nbr_operator = nbr_operator
        self.futur_length = futur_length
        
        self.formulation = formulation
        
        
        self.historic_operator = []
        self.historic_time = []
        self.job_launched = False
        

        self.target_date = []
        self.formulations = []
        
        self.echu_weights = echu_weights
        self.forward_weights = forward_weights
        self.ordo_weights = ordo_weights
        self.job_finished_weigths = job_finished_weigths
        
        self.number_echu = 0
        #params
        
        #list to keep the jobs objects
        self.job = Job(job_name,1, formulation, 20000, nbr_operation_max,target,target ,melange_number =0)
        
        #list to keep the machines objects
        self.machines = self.create_machines()
        
        #all the actions we can take
        self.actions_space = self.create_actions_space()
        
        #state size
        self.state_size = self.get_state_size()
        
        #assuming that the new batch begin with noting in the prod_line yet. TODO change this for more generic beahvior
        self.state_full = futur_state
                        
        self.time = target + DateOffset(hours = 12*4, minutes = -1)
        
        self.init_time = self.time
        self.morning_afternoon = 1 #0: morning, 1: afternoon
        self.reset()
    
    def reset(self):
        
        self.job.started = True     
        self.update_check_executable()
        
        
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
        
        if self.check_legality(action) == False:
            print("problem")
        #si l'action est légal, normalement elle l'est du au mask
        if self.check_legality(action):
            job_to_schedule = action[0]
            operation_to_schedule = action[1]
            machine_to_schedule = action[2]
            
            #print(self.operator[-1])
            #print(self.time.weekday())
                 
            if action == "forward":
                         
                self.historic_operator.append(self.state_full.loc[self.time]["operator"])             
                
                previous_time = self.time
                self.time -= DateOffset(hours= 12)
                futur_time = self.time -DateOffset(hours = 12*(self.futur_length-1))
                
                self.historic_time.append(self.time)
                
                #add new day to df
                if futur_time not in self.state_full.index:
                    self.state_full = self.add_timestep(self.state_full)
                
                #update and check expiration time of all operations
                self.number_echu = self.update_check_expiration_time(previous_time)
                
                reward += self.forward_weights
                
                #incremente lead_time for all job
                self.job.increment_lead_time()                          

                reward += self.echu_weights * self.number_echu # a tester, pour éviter les doublons
                
                #update the processing time of all operation and remove the op from
                #machine if the op has ended
                ended_operations = self.update_processing_time() 
                
                if self.number_echu:
                    
                    self.job.remove_all_operation()
                    self.job.ended = True
                
                
                                                     
            
            else:
                
                reward += self.ordo_weights
                
                #on set l'opération à "en cours", set the start time and the machine
                self.job.operations[operation_to_schedule-1].status = 1
                self.job.operations[operation_to_schedule-1].end_time = self.time
                self.job.operations[operation_to_schedule-1].processed_on = machine_to_schedule
                
                
                #update the machine status
                self.machines[machine_to_schedule-1].assign_operation(job_to_schedule,operation_to_schedule)
                
                #decrease the number of operator remaining
                op_duration = self.job.operations[operation_to_schedule-1].processing_time-1
                end_op = self.time - DateOffset(hours = 12*op_duration)
                machine_name = "m"+ str(self.machines[machine_to_schedule-1].number)


                self.state_full.loc[self.time:end_op,"operator"]  -= self.job.operations[operation_to_schedule-1].operator
                self.state_full.loc[self.time:end_op,machine_name] = self.machines[machine_to_schedule-1].status
                
        #update and check newly executable operations
        executables = self.update_check_executable()
        
        
        
        next_state = self.get_state()
        
        done = self.check_done() 
        
        if done and self.number_echu == 0:
            self.job.remove_all_operation()
            self.job.ended = True
            reward += self.job_finished_weigths
               
                
        return next_state,reward, done, self.number_echu
    
    
        
       
    def create_timeseries(self,target, futur_state):
        
        perry_duration = int(self.job.operations[15-1].processing_time/2)
        end = target + DateOffset(days = perry_duration)
        
        if futur_state is None:
            start = end - DateOffset(days = self.futur_length/2)
        else:
            start = target
            
        date_rng = pd.date_range(start=start, end=end, freq='12H', )
        date_rng = reversed(date_rng)
        df = pd.DataFrame(date_rng, columns=['date'])
        df['datetime'] = pd.to_datetime(df['date'])
        df = df.set_index('datetime')
        df.drop(['date'], axis=1, inplace=True)
        df = df.resample('12H', offset = '-1m').mean().iloc[::-1]
        
        
        df["operator"] = 0
        for index, row in df.iterrows():
            if index.dayofweek < 5:

                df.loc[index,"operator"] = self.nbr_operator
                          
        
        df["m1"] = 0
        df["m2"] = 0
        df["m3"] = 0
        df["m4"] = 0
        df["m5"] = 0
        df["m6"] = 0
        df["m7"] = 0
        df["m8"] = 0
        
        
        return df
        
    def merge_state(self, current, futur):
        
        df_tot = pd.concat([futur,current])    
        df_tot = df_tot.resample('12H', offset = '-1m').mean().iloc[::-1]
        
        for index, row in df_tot[df_tot["operator"].isna()].iterrows():
            if index.dayofweek < 5:
                df_tot.loc[index,"operator"] = 12
            else:
                df_tot.loc[index,"operator"] = 0
            
            df_tot.loc[index,"m1"] = 0
            df_tot.loc[index,"m2"] = 0
            df_tot.loc[index,"m3"] = 0
            df_tot.loc[index,"m4"] = 0
            df_tot.loc[index,"m5"] = 0
            df_tot.loc[index,"m6"] = 0
            df_tot.loc[index,"m7"] = 0
            df_tot.loc[index,"m8"] = 0
            
        return df_tot
    
    def create_machines(self):
        """
        create all the Machine objects

        """
        batch_description = get_batch_description()
        
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
            
            for machine in value:
                actions.append((1,int(key),machine))
        actions.append("forward")
        return actions
            
    
    
    
    
    def update_processing_time(self):
        
        ended_operations = []
        
        
        for operation in self.job.operations:
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
           
    def update_check_expiration_time(self,time):
        
        nbr_echu = 0
        
        for operation in self.job.operations:
            if operation != None:    
                #si l'opération est terminée
                if operation.status == -1:
                                  
                    for operation_used in operation.used_by:
                        #si l'opérations suivantes n'a pas encore commencé
                        if self.job.operations[operation_used-1].status == 0:
                    
                            #si l'opération est échue
                            if self.job.operations[operation_used-1].decrease_get_expiration_time(time) == 0:

                                job_ended = True
                                

                                nbr_echu += 1
                                self.job.echu += [operation_used]
                                
                                break           
                                        
        return nbr_echu
    
                     
    def update_check_executable(self):
        executables = []
        
        for operation in self.job.operations:
            if operation != None:
                if operation.status == 0: #and operation.executable == False:
                    executable = True
                    for dependencie in operation.dependencies:
                        #si l'opération précédente n'est pas terminée
                        if self.job.operations[dependencie-1].status != -1:
                            executable = False
                    
                    
                    duration = operation.processing_time
                    
                    #L'opération doit commencer le matin
                    if operation.begin_day == 1:
                        begin_time = self.time -DateOffset(hours = 12*(duration))
                        if begin_time.time().hour == 11:
                            executable = False
                        
                    if operation.QC_delay >0:
                        executable = False
                    
                    end_op = self.time - DateOffset(hours = 12*(duration-1))
                    state = self.state_full.loc[self.time:end_op]
                    #iter over the time of manufacturing for an operation
                    for i,row in state.iterrows():
                        if row["operator"] < operation.operator:
                            executable = False
                        
                        
                            
                    #check if machine is free for the whole process time
                    machine_free = np.full((len(operation.processable_on), duration), True)
                    for i,machine_number in enumerate(operation.processable_on):
                        machine_name = "m" + str(machine_number)
                        
                        for j,(index,row) in enumerate(state.iterrows()):
                            if row[machine_name] != 0:
                                machine_free[i,j] = False
                    if np.all(machine_free, axis=1).any() == False:
                        executable = False
                    
                        
                    #TODO change the static rule
                    #eviter que qu'un mélange d'un autre lot se produise pendant une extrusion, 7-8 extrusion, 5-6 mélange
                    if operation.operation_number == 7 or operation.operation_number == 8:
                        #on check que le mélangeur soit idle
                        if self.machines[3].status != 0:
                            executable = False
                    #same for melange
                    if operation.operation_number == 5 or operation.operation_number == 6:
                        #on check que le mélangeur soit idle
                        if self.machines[4].status != 0:
                            executable = False
                            
                    #TODO change this 
                    #pour eviter que l'extrusion soit mal plannifiée (probleme de doublon)
                    if operation.operation_number == 8 or operation.operation_number == 7:
                        if self.time.weekday() == 0:
                            executable = False
                        
                    
                    if executable:
                        executables.append(operation.operation_number)
                    operation.executable = executable
                #si op = perry
                        
        return executables
                        
    
                                
    def check_done(self):
        
        done = True
          
        for operation in self.job.operations:
            if operation != None:    
                if not (operation.status == -1):
                    done = False

        return done
                                
        
    
    def check_legality(self,action):
        
        if action == "forward":
            return True
        job_to_schedule = int(action[0])
        operation_to_schedule = int(action[1])
        machine_to_schedule = int(action[2])
        
        
        operation = self.job.operations[operation_to_schedule-1]
        
        if operation != None:
            duration = operation.processing_time
            
            #check if machine is free for the whole process time
            machine_name = "m" + str(machine_to_schedule)
            end_op = self.time - DateOffset(hours = 12*(duration-1))
            state = self.state_full.loc[self.time:end_op]
            machine_free = True
            for index,row in state.iterrows():
                if row[machine_name] != 0:
                    machine_free = False
                    
                #eviter que qu'un mélange d'un autre lot se produise pendant une extrusion
                melangeur_free = True
                if operation.operation_number == 7 or operation.operation_number == 8:
                    #on check que le mélangeur soit idle
                    if row["m4"] != 0:
                        melangeur_free = False
                 
            if operation.status == 0 and operation.executable and machine_free and melangeur_free:
                return True
                
        return False
    
    def get_mask(self):
        
        mask = []
        for action in self.actions_space:
            mask.append(self.check_legality(action))    

        return mask
    
    def get_state_size(self):
        
        params_op = 2
        params_machine = 1
        params_prod_line = 2
        state_size =  self.nbr_operation_max * params_op + self.futur_length*(self.nbr_machines * params_machine + 1) + params_prod_line
        
        
        return state_size
    
    def get_state(self):
        
        sum_state = np.array([])
        
        for operation in self.job.operations:
            if operation != None:
                sum_state = np.concatenate((sum_state, operation.get_state()))
            else:
                #default state
                sum_state = np.concatenate((sum_state, np.array([-1,-1])))
                              
        #add futur state to state 
        current_time = self.time
        futur_time = current_time - DateOffset(hours = 12*(self.futur_length-1))
        current_state = self.state_full.loc[current_time:futur_time]
        
        for row in current_state.to_numpy():
            row_copy = np.copy(row)
            row_copy[0] = row_copy[0]/self.nbr_operator
            sum_state = np.concatenate((sum_state,row))
        
        sum_state = np.concatenate((sum_state, np.array([self.morning_afternoon,(self.time.weekday()-3)/3])))
        
    
        assert(self.state_size == len(sum_state))
        
        
        return sum_state
    
    def get_gant_formated(self):
        planning = []
        
        planning.append(self.job.build_gant_formated())
                
        plan_df = pd.DataFrame()
        for plan in planning:
            df = pd.DataFrame(plan, columns =['Job','Machine', 'Operation', 'Start','Duration','Finish'])
            plan_df = pd.concat([plan_df, df], axis=0)
        
        plan_df.reset_index(drop = True,inplace=True)
        
        plan_df['Machine']= plan_df['Machine'].astype(str)
        plan_df['Duration']= plan_df['Duration']
            
        return plan_df
    
        
        
        #TODO summarize all the stats and kpis of the prod line
    
    def add_timestep(self,df):
        idx = df.tail(1).index[0] -  pd.Timedelta(hours=12)
        df.loc[idx] = [0,0,0,0,0,0,0,0,0]
        df = df.resample('12H', offset = '-1m').mean().iloc[::-1]
        
        if df.index[-1].dayofweek<5:
            df.loc[idx]["operator"] = 12
        
        return df            
            
        

   
        
        
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
    def job(self):
        return self.__job
    @job.setter
    def job(self, value):
        self.__job = value 
        
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
        
    
                        
        