# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 09:51:07 2022

@author: LDE
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 12:50:34 2021

@author: LDE
"""
from src.Operation3 import Operation
import numpy as np
import pandas as pd


class Job:
    
    def __init__(self,job_name, formulation, scale ,melange_number =0):
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
        self.scale = scale
        self.melange_number = melange_number
        
        #stats params
        self.lead_time = 0 #lead time in timestep
        self.started = False
        self.ended = False
        
        
        self.operations = []
        
        
    def build_gant_formated(self):
        
        planning = []
        for operation in self.operation_planning:
            if operation != None:
                job_name = operation.job_name
                operation_number = operation.operation_number
                machine = operation.processed_on
                start = operation.start_time
                end = operation.end_time
                try:
                    duration = end-start
                except:
                    duration  = 0.0
                planning.append((job_name,machine,operation_number,start,duration,end))
        return planning
    
