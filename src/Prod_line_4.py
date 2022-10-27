# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 10:29:00 2021

@author: LDE
"""

from Operation3 import Operation

import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset

import os

import get_batch_to_produce as btp
import src.utils as utils
import operator_stats as op_stats



abspath = os.path.abspath(__file__)
dname =os.path.dirname(os.path.dirname(abspath))
os.chdir(dname)

class Production_line():
    
    def __init__(self, current_date):
        
        
        """
        variables to keep trace of the data
        """
        self.historic_operator = []
        self.historic_time = []
        self.number_echu = 0
        
        self.job_launched = False
        
        self.time = current_date
        
        #READ the excel file and get all ressources for the whole year
        self.df, self.df_restricted = utils.unmerge_excel("data/Planning_Production 2022_13.10.2022.xlsm")

        self.operation_to_plan = btp.get_batch_to_plan(self.df, current_date) 
        
        self.vertices, self.adjacency = btp.get_operations_graph(self.operation_to_plan)

        
        #get the disponibility of ressources
        self.df_machine, self.df_operator = utils.extract_machine_operator_state(self.df_restricted)
        
        #PIF of all operators
        self.operator_stats_df = op_stats.get_PIF()
        
        #the operators that can operate the operations to produce
        self.operator_that_can_operate = btp.get_operators_for_operations(self.vertices, self.operator_stats_df)
        
        self.operations = []
        self.idx_operations_executable = np.full((len(self.vertices),),False )
        for i, op in enumerate(self.vertices):
            job_name = op[0]
            operation_name = op[1][0]
            formulation = op[1][1]
            scale = op[1][3]
            op_begin = op[1][5]
            op_end = op[1][6]
            done = op[1][7]
            if done:
                done = -1 #mean that the operation status is done
            else:
                done = 0 #mean that the operation status has not began yet
                
            if formulation == 6 and operation_name in ["BR", "TP", "MEL", "EX", "BB", "TM"]:
                operation_name = operation_name + "_" + op[1][2][-1] #to get the fraction 1 or 2 
                
            self.operations.append(Operation(job_name,operation_name,formulation,scale, op_begin, op_end, executable = False, status = done))
        
        
        
        self.update_executable()

        
        
        
    def step(self):

        

        
        pass
            
    
    
    #check only if the precedent operations have been made
    def update_executable(self):
        
        operators_dispo = self.get_available_operators()
        machines_dispo = self.get_available_machines()
        
        
        for index, operation in enumerate(self.operations):
            dependence_index = np.argwhere(self.adjacency [:,index] == 1)
            executable = True
            if len(dependence_index):
                for idx in dependence_index:
                    dependence = self.operations[idx[0]]
                    if dependence.status != -1: #si la dépendence n'est pas terminée
                        executable = False
                    if dependence.status == -1: #si la dépendance est terminée
                        if dependence.op_end > self.time: #si la dépendence n'est pas encore terminée dans notre timestamps
                            executable = False
                        
            if operation.status == -1 or operation.status == 1:#si l'opération est terminée ou en cours, elle n'est plus executable
                executable = False
                
            #ici nous avons deja checké si les étapes précédentes sont effectuée
            #on continue a checker si executable uniquement sur les opérations 
            #encore en course
            if executable:
                processing_time = operation.processing_time
                processable_on = operation.processable_on
                operator_needed = operation.operator
                begin_day = operation.begin_day
                
                #list des dates nécessaire à l'opération
                date_needed = []
                for i in range(processing_time):
                    futur_date = self.time + DateOffset(hours = i*12)
                    date_needed.append(futur_date)
                
                
                #begin with the machines
                dispo = np.full((len(processable_on), len(date_needed)),False)
                for k,machine_prob in enumerate(processable_on):
                    for l,d in enumerate(date_needed):
                        if machine_prob in machines_dispo[d]:
                            dispo[k,l] = True
                          
                if not dispo.all(axis = 1).any():
                    executable = False
                
                
                #check if the operators are available
                qualified_operator = self.operator_that_can_operate[index]
                
                dispo = np.full((len(date_needed)), False)
                for k, d in enumerate(date_needed):
                    dispo[k] = len(set(qualified_operator) & set(operators_dispo[d])) >= operator_needed
                    
                if not dispo.all():
                    executable = False
                     
            
            operation.executable = executable
            self.idx_operations_executable[index] = executable
        
        
       
    
    def get_available_operators(self):
        
        operators = self.df_operator[self.time:]

        operators_dispo = {}
        for index, op in operators.iterrows():
            if index.weekday() < 5:
                operators_dispo[index] = op.where(op == "0").dropna().index.tolist()
            else:
                operators_dispo[index] = []
                
        return operators_dispo
        
    def get_available_machines(self):
       
        machines = self.df_machine[self.time:]
        
        machines_dispo = {}
        for index, machine in machines.iterrows():
            if index.weekday() < 5:
                machines_dispo[index] = machine.where(machine == 0).dropna().index.tolist()
            else:
                machines_dispo[index] = []
                
        return machines_dispo

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
                        self.machines[machine].remove_operation()
                                
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
                        if self.job.operations[operation_used].status == 0:
                    
                            #si l'opération est échue
                            if self.job.operations[operation_used].decrease_get_expiration_time(time) == 0:

                                job_ended = True
                                

                                nbr_echu += 1
                                self.job.echu += [operation_used]
                                
                                break           
                                        
        return nbr_echu
    

    
    
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
        
    
                        
        