# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 11:07:14 2021

@author: LDE
"""

class Machine:
        def __init__(self,number,name):
            self.number = number
            self.name = name
            self.status = 0 # 0:idle, 1:attribué 2:panne
            self.operation = (0,0)
                        
        def change_status(self,new_status):
            self.status = new_status
            
        def get_status(self):
            return self.status
        
        def assign_operation(self,operation):
            self.operation = operation
            if self.status != 2:
                self.change_status(1)
                return True
            return False
            
        def get_operation(self):
            return self.operation
        
        def get_number(self):
            return self.number
        
        def remove_operation(self):
            self.job = None
            if self.status != 2:
                self.status =0
            self.operation = (0,0)
                
        def get_state(self):
            return {
                "machine" : self.number,
                "status" : self.status,
                "operation" : self.operation
                }
                
        