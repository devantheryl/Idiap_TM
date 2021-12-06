# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 12:50:34 2021

@author: LDE
"""

import numpy as np
import json


class Job:
    
    def __init__(self,job_name, formulation, job_size, max_operation, melange_number =0):
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
        self.formulation = formulation
        self.job_size = job_size
        self.max_operation = max_operation
        self.melange_number = melange_number
        
        #stats params
        self.lead_time = 0
        
        #game plate 
        self.operations = np.full(max_operation,None)
        self.create_all_operations()
        
        
        
        
    def create_all_operations(self):
        
        with open("src/batch_description.json") as json_file:
            batch_description = json.load(json_file)
            
        if self.formulation == 1 and self.job_size == 20000:
            
            batch_info = batch_description["Batch_3.75_20000"]
            for key, value in batch_info.items():
                number = value["number"]
                processable_on = value["processable_on"]
                processing_time = value["processing_time"]
                expiration_time = value["expiration_time"]
                dependencies = value["dependencies"]
                executable = False
                operator = value["operator"]
                used_by = value["used_by"]
                if number == 1 or number == 7:
                    executable = True
                    
                #to change
                operation = Operation(self.job_name,operation_number,processable_on,processing_time,nbr_of_sucessor,expiration_time,dependencies,operator,used_by,executable)
                self.operations[number-1] = operation
                
    def increment_lead_time(self, increment):
        self.lead_time += increment
    def get_lead_time(self):
        return self.lead_time
    
    
        
        