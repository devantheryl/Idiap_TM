# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 11:56:38 2021

@author: LDE
"""
from src.Operation import Operation
import networkx as nx 
import json
import os

#to set the current working directory
os.chdir("C:/Users/LDE/Prog/DigitalTwins/planning auto/Digital_twins")



operations_formu_1_3 = [1,2,3,4,5,6,7,9,10,11,12,13,14]
edges_formu_1_3 = [(1,2),(2,3),(3,4),(4,5),(5,6),(6,9),(7,9),(9,10),(10,11),(11,12),(12,13),(13,14)]

operations_formu_6 = [1,1,2,2,3,3,4,4,5,5,6,6,7,8,9,10,11,12,13,14]

with open("src/batch_description.json") as json_file:
    batch_description = json.load(json_file)
    

class Job:
    
    def __init__(self,job_name,formulation,job_size,priority = 0, melange_number = 0):
        
        self.job_name = job_name
        self.formulation = formulation
        self.job_size = job_size
        self.priority = priority
        self.melange_number = melange_number
        self.operations = []  
        self.lead_time = 0
        
        self.create_all_operations()
          
      
    
    def get_job_name(self):
        return self.job_name
      
    def create_all_operations(self):
        
        if self.formulation == 1 and self.job_size == 20000:
            
            batch_info = batch_description["Batch_3.75_20000"]
            for operation_number in operations_formu_1_3:
                
                operation = "operation" + str(operation_number)
                
                processable_on = batch_info[operation]["processable_on"]
                processing_time = batch_info[operation]["processing_time"]
                nbr_of_sucessor = batch_info[operation]["nbr_of_sucessor"]
                expiration_time = batch_info[operation]["expiration_time"]
                dependencies = batch_info[operation]["dependencies"]
                executable = False
                operator = batch_info[operation]["operator"]
                used_by = batch_info[operation]["used_by"]
                if operation_number == 1:
                    executable = True
                operation = Operation(self.job_name,operation_number,processable_on,processing_time,nbr_of_sucessor,expiration_time,dependencies,operator,used_by,executable)
                self.operations.append(operation)
                
        #TODO add for the others type of batchs
        
        
            
    def get_all_operations(self):
        return self.operations
    
    def increment_lead_time(self,increment):
        self.lead_time += increment
    
    def build_gant_formated(self):
        
        planning = []
        for operation in self.operations:
            operation_number = operation.get_operation_number()
            machine = operation.get_processed_on()
            start = operation.get_start_time()
            end = operation.get_end_time()
            duration = end-start
            planning.append((self.job_name,machine,operation_number,start,duration,end))
        return planning
    
    def create_operation(self,operation_number):
        if self.formulation == 1 and self.job_size == 20000:
            #to change, more generic
            batch_info = batch_description["Batch_3.75_20000"]
            batch_info = batch_info["operation"+str(operation_number)]
            operation = "operation" + str(operation_number)
                
            processable_on = batch_info["processable_on"]
            processing_time = batch_info["processing_time"]
            nbr_of_sucessor = batch_info["nbr_of_sucessor"]
            expiration_time = batch_info["expiration_time"]
            dependencies = batch_info["dependencies"]
            executable = False
            operator = batch_info["operator"]
            used_by = batch_info["used_by"]
            if operation_number == 1:
                executable = True
            operation = Operation(self.job_name,operation_number,processable_on,processing_time,nbr_of_sucessor,expiration_time,dependencies,operator,used_by,executable)
            self.operations.append(operation)
        return operation
            



        