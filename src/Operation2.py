# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 17:15:04 2021

@author: LDE
"""

import numpy as np

class Operation:
    
    def __init__(self,job_name, operation_number, processable_on, processing_time,
                 expiration_time, dependencies, operator, used_by, QC_delay,begin_day,
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
        self.QC_delay = QC_delay
        self.begin_day = begin_day
        self.executable = executable
        self.status = 0 #0:non-attribué, 1:en cours, 2:terminé, 3:used, 4:doens't exist, 5 : attente QC
        
        #stats vars
        self.start_time = 0.0
        self.end_time = 0.0
        self.processed_on = 0
        
    def forward(self):
        
        if self.status == 1:
            self.processing_time-=1
            
        if self.status == 5:
            self.QC_delay -=1
            
        if self.processing_time == 0 and self.QC_delay == 0:
            self.status = 2
        else:
            self.status = 5
            
        return self.status
        
    def decrease_get_expiration_time(self):
        self.expiration_time -= 1
        return self.expiration_time
    
    def get_state(self):
        return self.status/5, self.processing_time/4, self.expiration_time/60, self.executable
    
    
    @property
    def job_name(self):
        return self.__job_name
    @job_name.setter
    def job_name(self, value):
        self.__job_name = value            

    @property
    def operation_number(self):
        return self.__operation_number
    @operation_number.setter
    def operation_number(self, value):
        self.__operation_number = value            
        
    @property
    def processable_on(self):
        return self.__processable_on
    @processable_on.setter
    def processable_on(self, value):
        self.__processable_on = value
    
    @property
    def processing_time(self):
        return self.__processing_time
    @processing_time.setter
    def processing_time(self, value):
        self.__processing_time = value          
    
    @property
    def expiration_time(self):
        return self.__expiration_time
    @expiration_time.setter
    def expiration_time(self, value):
        self.__expiration_time = value        
        
    @property
    def dependencies(self):
        return self.__dependencies
    @dependencies.setter
    def dependencies(self, value):
        self.__dependencies = value      
        
    @property
    def operator(self):
        return self.__operator
    @operator.setter
    def operator(self, value):
        self.__operator = value       
        
    @property
    def used_by(self):
        return self.__used_by
    @used_by.setter
    def used_by(self, value):
        self.__used_by = value 
           
    @property
    def QC_delay(self):
        return self.__QC_delay
    @QC_delay.setter
    def QC_delay(self, value):
        self.__QC_delay = value 
        
    @property
    def executable(self):
        return self.__executable
    @executable.setter
    def executable(self, value):
        self.__executable = value     
        
    @property
    def status(self):
        return self.__status
    @status.setter
    def status(self, value):
        self.__status = value   
        
    @property
    def start_time(self):
        return self.__start_time
    @start_time.setter
    def start_time(self, value):
        self.__start_time = value
             
    @property
    def end_time(self):
        return self.__end_time
    @end_time.setter
    def end_time(self, value):
        self.__end_time = value
        
    @property
    def processed_on(self):
        return self.__processed_on
    @processed_on.setter
    def processed_on(self, value):
        self.__processed_on = value
        
        