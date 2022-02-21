# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 12:50:34 2021

@author: LDE
"""
from src.Operation2 import Operation
import numpy as np
import json
from datetime import datetime, timedelta, date


class Job:
    
    def __init__(self,job_name,job_number, formulation, job_size, max_operation,target_date,creation_date ,melange_number =0):
        """
        init a new Job and create all corresponding operations

        Parameters:
            job_name (Str) : the job's name
            formulation (int) : formulation of the product (1, 3 or 6)
            job_size (int) : the echel of the job (6600 or 20000)
            max_operations (int) : the number max of operations per job (normaly = 14)
            melange_number (int) : the number of melange
        """
        
        #init params
        self.job_name = job_name
        self.job_number = job_number
        self.formulation = formulation
        self.job_size = job_size
        self.max_operation = max_operation
        self.melange_number = melange_number
        self.target_date = target_date
        self.creation_date = creation_date
        
        
        #stats params
        self.lead_time = 0
        self.started = False
        self.ended = False
        
        
        self.operation_planning = []
        
        #game plate 
        self.operations = np.full(max_operation,None)
        
        self.create_all_operations()
        
        
        
        
        
    def create_all_operations(self):
        
        with open("src/batch_description.json") as json_file:
            batch_description = json.load(json_file)
            
        if self.formulation == 1 and self.job_size == 20000:
            
            batch_info = batch_description["Batch_3.75_20000_REVERSE"]
            for key, value in batch_info.items():
                op_type = value["type"]
                if op_type == "operation":
                    number = value["number"]
                    processable_on = value["processable_on"]
                    processing_time = value["processing_time"]
                    expiration_time = value["expiration_time"]
                    dependencies = value["dependencies"]
                    executable = False
                    operator = value["operator"]
                    used_by = value["used_by"]
                    begin_day = value["begin_day"]
                    
                if op_type == "liberation":
                    number = value["number"]
                    processable_on = 0
                    processing_time = value["processing_time"]
                    expiration_time = 0
                    dependencies = value["dependencies"]
                    executable = False
                    operator = 0
                    used_by = value["used_by"]
                    begin_day = value["begin_day"]
                    
                #create the operation
                operation = Operation(self.job_name,op_type,number,processable_on,
                                      processing_time,expiration_time,
                                      dependencies,operator,used_by,begin_day,executable)
                
                #store it in the jobs array
                self.operations[number-1] = operation
                self.operation_planning.append(operation)
                
    def create_operation(self, operation_number):
        with open("src/batch_description.json") as json_file:
            batch_description = json.load(json_file)
        
        if self.formulation == 1 and self.job_size == 20000:
            
            batch_info = batch_description["Batch_3.75_20000_REVERSE"]
            for key, value in batch_info.items():
                if value["number"] == operation_number:
                    op_type = value["type"]
                    if op_type == "operation":
                        number = value["number"]
                        processable_on = value["processable_on"]
                        processing_time = value["processing_time"]
                        expiration_time = value["expiration_time"]
                        dependencies = value["dependencies"]
                        executable = False
                        operator = value["operator"]
                        used_by = value["used_by"]
                        begin_day = value["begin_day"]
                        
                    if op_type == "liberation":
                        number = value["number"]
                        processable_on = 0
                        processing_time = value["processing_time"]
                        expiration_time = 0
                        dependencies = value["dependencies"]
                        executable = False
                        operator = 0
                        used_by = value["used_by"]
                        begin_day = 1
                        
                    #create the operation
                    operation = Operation(self.job_name,op_type,number,processable_on,
                                          processing_time,expiration_time,
                                          dependencies,operator,used_by,begin_day,executable)
                    #store it in the jobs array
                    self.operations[operation_number-1] = operation
                    self.operation_planning.append(operation)
                    
                    return
        
                
    def increment_lead_time(self, increment=1):
        self.lead_time += increment
    
        
    def build_gant_formated(self):
        
        planning = []
        for operation in self.operation_planning:
            if operation != None:
                operation_number = operation.operation_number
                machine = operation.processed_on
                start = operation.start_time
                end = operation.end_time
                try:
                    duration = end-start
                except:
                    duration  = 0.0
                planning.append((self.job_name,machine,operation_number,start,duration,end))
        return planning
        
    @property
    def job_name(self):
        return self.__job_name
    @job_name.setter
    def job_name(self, value):
        self.__job_name = value  
        
        
    @property
    def job_number(self):
        return self.__job_number
    @job_number.setter
    def job_number(self, value):
        self.__job_number = value  
    
    @property
    def formulation(self):
        return self.__formulation
    @formulation.setter
    def formulation(self, value):
        self.__formulation = value  
    
    @property
    def job_size(self):
        return self.__job_size
    @job_size.setter
    def job_size(self, value):
        self.__job_size = value      
        
    @property
    def max_operation(self):
        return self.__max_operation
    @max_operation.setter
    def max_operation(self, value):
        self.__max_operation = value  
        
    @property
    def melange_number(self):
        return self.__melange_number
    @melange_number.setter
    def melange_number(self, value):
        self.__melange_number = value  
        
    @property
    def target_date(self):
        return self.__target_date
    @target_date.setter
    def target_date(self, value):
        self.__target_date = value 
        
    @property
    def lead_time(self):
        return self.__lead_time
    @lead_time.setter
    def lead_time(self, value):
        self.__lead_time = value  
        
    
        
    @property
    def started(self):
        return self.__started
    @started.setter
    def started(self, value):
        self.__started = value 
        
    @property
    def operations(self):
        return self.__operations
    @operations.setter
    def operations(self, value):
        self.__operations = value  