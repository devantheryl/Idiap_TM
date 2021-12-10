# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 11:51:52 2021

@author: LDE
"""


class Machine:
    
    def __init__(self, number, name):
        
        self.number = number
        self.name = name
        
        #params
        self.status = 0 #0: idle, 1: attribué, 2: panne
        self.operation = 0 #0 = pas d'opération
        self.job = 0 #0 = pas de job
        
        
    def assign_operation(self,operation):
        
        self.operation = operation
        if self.status == 0:
            self.change_status(1)
            return True
        return False
    
    def remove_operation(self):
    
        self.job = 0
        self.operation = 0
        
        if self.status == 1:
            self.status =0
            return True
        return False
    
    def get_state(self):
        return self.status, self.job, self.operation
    
    
    
    @property
    def number(self):
        return self.number
    @number.setter
    def number(self, value):
        self.number = value      
        
    @property
    def name(self):
        return self.name
    @name.setter
    def name(self, value):
        self.name = value     
        
    @property
    def status(self):
        return self.status
    @status.setter
    def status(self, value):
        self.status = value     
        
    @property
    def operation(self):
        return self.operation
    @operation.setter
    def operation(self, value):
        self.operation = value     
        
    @property
    def job(self):
        return self.job
    @job.setter
    def job(self, value):
        self.job = value     
        
            