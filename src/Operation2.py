# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 17:15:04 2021

@author: LDE
"""

import numpy as np

class Operation:
    
    def __init__(self,job_name, operation_number, processable_on, processing_time,
                 expiration_time, dependencies, operator, used_by, 
                 executable = False, status = 0):
        
        #init variable
        self.job_name = job_name
        self.operation_number = operation_number
        self.processable_on = processable_on
        self.processing_time = processing_time
        self.expiration_time = expiration_time
        self.dependencies = dependencies
        self.operator = operator
        self.used_by = used_by
        self.executable = executable
        self.status = 0 #0:non-attribué, 1:en cours, 2:terminé, 3:used, 4:doens't exist
        
        #stats vars
        self.start_time = 0.0
        self.end_time = 0.0
        self.processed_on = 0
        
        def forward(self):
            self.processing_time-=1
            if self.processing_time == 0:
                self.status = 2
            
        def decrease_get_expiration_time(self):
            self.expiration_time -= 1
            return self.expiration_time