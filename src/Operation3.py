# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 17:15:04 2021

@author: LDE
"""

import numpy as np

from batch_description_2 import get_batch_description


batch_description = get_batch_description()

class Operation:
    
    def __init__(self,job_name,operation_name,formulation,scale, op_begin, op_end,  executable = False, status = 0):
        
        self.job_name = job_name
        self.operation_name = operation_name
        self.formulation = formulation
        self.scale = scale
        self.op_begin = op_begin
        self.op_end = op_end
        self.executable = executable
        self.status = status #0:non-attribué, 1:en cours, -1:terminé
        

        self.processable_on = batch_description[str(formulation) + "_" + str(scale)][operation_name]["processable_on"]
        self.processing_time = batch_description[str(formulation) + "_" + str(scale)][operation_name]["processing_time"]
        self.expiration_time = batch_description[str(formulation) + "_" + str(scale)][operation_name]["expiration_time"]
        self.operator = batch_description[str(formulation) + "_" + str(scale)][operation_name]["operator"]
        self.begin_day = batch_description[str(formulation) + "_" + str(scale)][operation_name]["begin_day"]
        self.QC_delay = batch_description[str(formulation) + "_" + str(scale)][operation_name]["QC_delay"]
        
        
        
    def forward(self):
    
        #op en cours
        if self.status == 1:
            self.processing_time -= 1
                   
        if self.processing_time == 0:
            self.status = -1
            
        return self.status
        
    def decrease_get_expiration_time(self, time):
        self.expiration_time -= 1
        if time.weekday() <5 and self.QC_delay >0:
            self.QC_delay -=1
        return self.expiration_time
    
    
        
        