# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 10:29:00 2021

@author: LDE
"""

from Operation3 import Operation
from Job4 import Job
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
    
    def __init__(self, current_date, excel_file):
        
        
        """
        variables to keep trace of the data
        """
        operation_machine = {
            "Broyage polymère B1" : "m0",
            "Broyage polymère B2" : "m1",
            "Tamisage polymère B2": "m2",
            "Mélanges B2" : "m3",
            "Mélanges B1 " : "m9",
            "Extrusion B2" :  "m4",
            "Broyage bâtonnets B1 " : "m0",
            "Broyage bâtonnets B2 " : "m1",
            "Tamisage Microgranules B2" :"m2",
            "Milieu de suspension  " : "m6",
            "Remplissage Poudre + liquide B2" : "m7",
            "Combin. des fractions de microgranules" : "m5",
            "Capsulage" : "m8"
            }
        
        self.excel_file = excel_file
        self.historic_operator = []
        self.historic_time = []
        self.nbr_echu = 0
        
        self.job_launched = False
        
        self.begin_time = current_date
        self.time = current_date
        
        #READ the excel file and get all ressources for the whole year
        self.df, self.df_restricted = utils.unmerge_excel(self.excel_file)

        self.operation_to_plan = btp.get_batch_to_plan(self.df,self.df_restricted, current_date) 
        
        self.IV_to_plan = btp.get_IV_occupations(self.df,self.df_restricted, current_date)
        
        self.vertices, self.adjacency = btp.get_operations_graph(self.operation_to_plan, {})

        
        #get the disponibility of ressources
        self.df_machine, self.df_operator = utils.extract_machine_operator_state(self.df_restricted)
        
        #PIF of all operators
        self.operator_stats_df, self.operator_list = op_stats.get_PIF()
        
        #the operators that can operate the operations to produce
        self.operator_that_can_operate = btp.get_operators_for_operations(self.vertices, self.operator_stats_df)
        
        self.operations = []
        self.idx_operations_executable = np.full((len(self.vertices),),False )
        
        #create a list of all batches to plan
        self.batch_names = []
        for op in self.vertices:
            self.batch_names.append([op[0], op[1][1], op[1][3]])#add all the batch name, formu, scale
 
        self.batch_names = np.unique(self.batch_names, axis = 0)
 
        #create a list of Job using the batch_names
        self.jobs = {}
        for batch in self.batch_names:
            self.jobs[batch[0]] = Job(batch[0],batch[1], batch[2])
        
        
        for i, op in enumerate(self.vertices):
            job_name = op[0]
            operation_name = op[1][0]
            formulation = op[1][1]
            scale = op[1][3]
            op_begin = op[1][5]
            op_end = op[1][6]
            done = op[1][7]
            try:
                processed_on = operation_machine[op[1][8]]
            except:
                processed_on = None
            if done:
                done = -1 #mean that the operation status is done
            else:
                done = 0 #mean that the operation status has not began yet
                
            if formulation == 6 and operation_name in ["BR", "TP", "MEL", "EX", "BB", "TM"]:
                operation_name = operation_name + "_" + op[1][2][-1] #to get the fraction 1 or 2 
            operation = Operation(job_name,operation_name,formulation,scale, op_begin, op_end,self.operator_that_can_operate[i], processed_on,executable = False, status = done)
            self.operations.append(operation)
            self.jobs[job_name].operations.append(operation)
            
        #create lookup table to speed up the computation
        self.dependence_index_lookup = []
        self.used_by_index_lookup = []
        for index, operation in enumerate(self.operations):  
            self.dependence_index_lookup.append(np.argwhere(self.adjacency [:,index] == 1))
            self.used_by_index_lookup.append(np.argwhere(self.adjacency[index,:] == 1))
        
            
        self.current_batch_on_IV = None
        self.machines_dispo = None
        self.operators_dispo = None
        
        
        
        
        

        
        
    """
    fonction pour avancer toutes les opérations d'un timestep.
    """
    def forward(self):
        echu = []
        too_late = []
        self.time += DateOffset(hours = 12)
        for index, operation in enumerate(self.operations):
            
            dependence_index = self.dependence_index_lookup[index]
            used_by_index = self.used_by_index_lookup[index]


            #check if the already planned operation is not executed before the one on which it depends
            for idx in dependence_index:
                dependence = self.operations[idx[0]]
                if operation.status == -1 and dependence.status != -1:
                    if operation.op_begin < self.time:
                        too_late.append(dependence)
            
                            
            #check if the following operation are finished or planned to decrease the expiration time of the current one
            used_by_done = True
            for idx in used_by_index:
                used_by = self.operations[idx[0]]
                if used_by.status ==0 :
                    used_by_done = False
                    
            #si les opérations suivantes ne sont pas toutes terminée et que celle en cours est terminée
            if not used_by_done and operation.status == -1:
                expiration_time = operation.decrease_get_expiration_time(self.time)
                if expiration_time == -1: #si l'opération est échue
                    echu.append(operation)
            
            #forward the opération
            operation.forward(self.time)
            
        self.nbr_echu += len(echu)
        
        #check if the IV si already taken
        current_batch_on_iv = self.df_restricted.loc[self.time]["Inspection visuelle "]
        if  current_batch_on_iv == "0":
            self.current_batch_on_IV = None
        else:
            self.current_batch_on_IV = current_batch_on_iv
        
        if len(too_late):
            print(too_late[0].operation_name, " too late")
        if len(echu):
            print(echu[0].operation_name, " echu")
            
        return echu + too_late
            
    
    
    #check only if the precedent operations have been made
    def update_executable(self):
        
        self.operators_dispo = self.get_available_operators(self.time)
        self.machines_dispo  = self.get_available_machines(self.time)
        
        
        for index, operation in enumerate(self.operations):
            
            
            
            dependence_index = self.dependence_index_lookup[index]
            used_by_index = self.used_by_index_lookup[index]
            executable = True
            
            if operation.operation_name == "MEL" and self.time.weekday() > 4:
                executable = False
            
            #check si la dépendance est finie
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
                
            #if the operation has to begin in the morning
            if self.time.hour == 12 and operation.begin_day:
                executable = False
                
                
            #ici nous avons deja checké si les étapes précédentes sont effectuée
            #on continue a checker si executable uniquement sur les opérations 
            #encore en course
            if executable:
                
                #check qu'il y ait pas trop d'écart entre l'opération en cours et la suivante 
                #si la suivante est deja terminée (aka deja plannifiée)
                if len(used_by_index):
                    for idx in used_by_index:
                        used_by = self.operations[idx[0]]
                        
                        if used_by.status == -1:
                            if self.time < (used_by.op_begin - DateOffset(hours = 12 * operation.expiration_time)):
                                executable = False
                                
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
                        if machine_prob in self.machines_dispo[d]:
                            dispo[k,l] = True
                          
                if not dispo.all(axis = 1).any():
                    executable = False
                
                
                #check if the operators are available
                qualified_operator = self.operator_that_can_operate[index]
                
                dispo = np.full((len(date_needed)), False)
                for d in date_needed:
                    qualified_operator = list(set(qualified_operator) & set(self.operators_dispo[d]))
                    
                if len(qualified_operator) < operator_needed:
                    executable = False
                    
                    
                #special_part for IV
                if not (self.current_batch_on_IV == None or self.current_batch_on_IV == operation.job_name):
                     executable = False
            
            operation.executable = executable
            self.idx_operations_executable[index] = executable
            
            
        return self.machines_dispo, self.operators_dispo
        
        
       
    
    def get_available_operators(self, time):
        
        vacances_conge2022 = ["2022-04-18","2022-05-26","2022-05-27", "2022-06-06","2022-06-16", "2022-08-01", "2022-08-15",
                          "2022-11-01", "2022-12-08", "2022-12-26","2022-12-27", "2022-12-28", "2022-12-29", "2022-12-30"]
        
        operators = self.df_operator[time:time+DateOffset(hours = 12*3)]
        
        operators_dispo = {}      
        for row in operators.itertuples():
            index = row[0]
            op = np.array(list(row[1:]))
            if index.weekday() < 5 and index.strftime("%Y-%m-%d") not in vacances_conge2022:
                operators_dispo[index] = np.take(self.operator_list, np.nonzero(op=="0")[0]).tolist()
            else:
                operators_dispo[index] = []
            pass
                
        return operators_dispo
        
    def get_available_machines(self, time):
       
        machines = self.df_machine[time:time+DateOffset(hours = 12*3)]
        
        machines_dispo = {}
        for row in machines.itertuples():
            index = row[0]
            op = np.array(list(row[1:]))
            if index.weekday() < 5:
                machines_dispo[index] = np.take(machines.columns, np.nonzero(op=="0")[0]).tolist()
            else:
                machines_dispo[index] = []
            pass
    
            machines_dispo[index].append("m10")
                
        return machines_dispo

    """
    check that all the batches are fully planned
    """
    def check_done(self):
        for operation in self.operations:
            if operation.status != -1: #si l'opération n'est pas terminée
                return False
        
        return True

    
    
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
    
    def get_lead_time(self):
        
        lead_times = []
        for i,job in self.jobs.items():
            begin = job.operations[0].op_begin
            end = job.operations[-1].op_end
            for op in job.operations:
                if begin > op.op_begin:
                    begin = op.op_begin
                if end < op.op_end:
                    end = op.op_end
            lead_time = end-begin
            
            lead_times.append(lead_time.days*2 + lead_time.seconds/3600/12)
                
                
                    
        return lead_times
    
            
  
        
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
        
    
                        
        