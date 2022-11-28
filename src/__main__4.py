# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 16:40:36 2022
@author: LDE
"""
from Prod_line_4 import Production_line
import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset



#from src.TF_env3 import TF_environment
#from tensorforce import Environment, Agent

import src.utils as utils



import place_operator as utils_operators
import place_operations as utils_operations

import operator_stats as op_stats
from Operation3 import Operation


import os

import get_batch_to_produce as btp
import src.utils as utils
import operator_stats as op_stats

from random import sample
from copy import deepcopy
from time import time

#load the current_date and create the prod_line object
begin_date = pd.to_datetime("2022-11-15", format = "%Y-%m-%d")
excel_file = "data/Planning Production 2022_15.11.22.xlsm"


prod_line = Production_line(begin_date,excel_file)


prod_line.operators_dispo = prod_line.get_available_operators(prod_line.time)
prod_line.machines_dispo  = prod_line.get_available_machines(prod_line.time)




now = time()
for t in range(1000):
    pass
    
print((time()-now)/1000)


operation_machine = {
    ("BR","m0") : "Broyage polymère B1",
    ("BR","m1") : "Broyage polymère B2",
    ("BR_1","m0") : "Broyage polymère B1",
    ("BR_1","m1") : "Broyage polymère B2",
    ("BR_2","m0") : "Broyage polymère B1",
    ("BR_2","m1") : "Broyage polymère B2",
    
    ("TP","m2") : "Tamisage polymère B2",
    ("TP_1","m2") : "Tamisage polymère B2",
    ("TP_2","m2") : "Tamisage polymère B2",
    
    ("MEL","m3") : "Mélanges B2",
    ("MEL_1","m3") : "Mélanges B2",
    ("MEL_2","m3") : "Mélanges B2",
    ("MEL","m9") : "Mélanges B1 ",
    ("MEL_1","m9") : "Mélanges B1 ",
    ("MEL_2","m9") : "Mélanges B1 ",

    
    ("EX","m4") : "Extrusion B2",
    ("EX_1","m4") : "Extrusion B2",
    ("EX_2","m4") : "Extrusion B2",
    
    ("BB","m0") : "Broyage bâtonnets B1 ",
    ("BB","m1") : "Broyage bâtonnets B2 ",
    ("BB_1","m0") : "Broyage bâtonnets B1 ",
    ("BB_1","m1") : "Broyage bâtonnets B2 ",
    ("BB_2","m0") : "Broyage bâtonnets B1 ",
    ("BB_2","m1") : "Broyage bâtonnets B2 ",
    
    ("TM","m2") : "Tamisage Microgranules B2",
    ("TM_1","m2") : "Tamisage Microgranules B2",
    ("TM_2","m2") : "Tamisage Microgranules B2",
    
    ("MILIEU","m6") : "Milieu de suspension  ",
    
    ("CF","m5") : "Combin. des fractions de microgranules",
    
    ("PERRY","m7") : "Remplissage Poudre + liquide B2",
    
    ("CAPS", None) : "Capsulage", 
    ("CAPS", "m8") : "Capsulage", 
    ("IV", "m10") : "Inspection visuelle "
    }
operation_raccourci = {
    "Broyage polymère B1" : "BR",
    "Broyage polymère B2" : "BR",
    "Tamisage polymère B2" :"TP",
    "Mélanges B2" : "MEL",
    "Extrusion B2" : "EX",
    "Broyage bâtonnets B1 " : "BB",
    "Broyage bâtonnets B2 " : "BB",
    "Tamisage Microgranules B2" : "TM",
    "Milieu de suspension  " : "MILIEU",
    "Combin. des fractions de microgranules" : "CF",
    "Sortie Lyo" : "LYO",
    "Capsulage" : "CAPS",
    "Remplissage Poudre + liquide B2" : "LYO",
    "Inspection visuelle " : "IV"
    
    }

operateur_needed = {
    "Broyage polymère B1" : 2,
    "Broyage polymère B2" : 2,
    "Tamisage polymère B2" :2,
    "Mélanges B2" : 3,
    "Extrusion B2" : 2,
    "Broyage bâtonnets B1 " : 2,
    "Broyage bâtonnets B2 " : 2,
    "Tamisage Microgranules B2" : 2,
    "Milieu de suspension  " : 2,
    "Combin. des fractions de microgranules" : 2,
    "Remplissage Poudre + liquide B2" : 8, 
    "Sortie Lyo" : 2,
    "Capsulage" : 2,
    "Inspection visuelle " :1
    }

#attribue les opérateurs aux opérations qui n'en ont pas encore 
operators = prod_line.df_operator[begin_date:]
machine = prod_line.df_machine[begin_date:]
operator_stats_df = prod_line.operator_stats_df

date_problem = []
for index in machine.index:
    machines_used = machine.loc[index]
    machines_used = machines_used[machines_used!="0"].to_list()
    
    
    best_ratio = 0
    best_attribution = None
    for tentative in range(50):
        #on crée une copie des opérateurs
        operators_planned = operators.loc[index].copy()
        total_needed = 0
        total_planned = 0
        
        #go through the used machines
        for machine_used in machines_used:
            machine_used_raccourci = operation_raccourci[machine_used]
            attributed_operator = operators_planned[(machine_used_raccourci == operators_planned) == True].to_list()
            free_operators = operators_planned.where(operators_planned == "0").dropna().index.tolist()
            
            #l'opération n'a pas encore d'opérateur attitrés
            if len(attributed_operator) == 0:
                operator_that_can_operate = operator_stats_df.loc[machine_used_raccourci][operator_stats_df.loc[machine_used_raccourci] == 1].index.tolist()
                free_operaotr_that_can_operate = list(set(operator_that_can_operate) & set(free_operators))
                nbr_operator_needed = operateur_needed[machine_used]
                
                total_needed += nbr_operator_needed
                for i in range(nbr_operator_needed,1,-1):
                    try:
                        selected_operator = sample(free_operaotr_that_can_operate,i)
                        for op in selected_operator:
                            operators_planned[op] = machine_used_raccourci
                        total_planned += i
                        break
                    except:
                        print("not enough operators")
                
        if total_needed == 0:
            break
            
        ratio = total_planned/total_needed
        if ratio > best_ratio:
            best_ratio = ratio
            best_attribution = operators_planned
        if ratio == 1:
            break
            
    if total_needed != 0:
        operators.loc[index] = best_attribution
        if best_ratio != 1:
            date_problem.append(index)
        
    
prod_line.df_operator[begin_date:] = operators   
    



nbr_tentative = 500
tentatives_prod_line = []
ocupation_operator_mean = []
for tentative in range(nbr_tentative):
    print("tentative : ", tentative)
    
    prod_line_tentative= deepcopy(prod_line)
    
    selected_machines  = {}
    done = False
    ocupation_operators = []
    
    while not done:
        current_date = prod_line_tentative.time
        machine_dispo, operator_dispo = prod_line_tentative.update_executable()
        
        executable_idx = []
        executable_operation = []
        smallest_exp_time = 100
        smallest_idx = None
        for index, op in enumerate(prod_line_tentative.operations):
            if op.executable:
                executable_idx.append(index)
                executable_operation.append(op)
                
                used_by_index = prod_line_tentative.dependence_index_lookup[index]
                if len(used_by_index) == 0:
                    if op.expiration_time < smallest_exp_time:
                        smallest_exp_time = op.expiration_time 
                        smallest_idx = index
                for used_by_idx in used_by_index:
                    used_by_op = prod_line_tentative.operations[used_by_idx[0]]
                    if used_by_op.expiration_time < smallest_exp_time:
                        smallest_exp_time = used_by_op.expiration_time 
                        smallest_idx = index
        
        if len(executable_idx) == 0:
            executable_idx.append("forward")
            choosen_idx = "forward"
        else:
            if smallest_exp_time > 6:
                choosen_idx = sample(executable_idx,1)[0]
            else:
                choosen_idx = smallest_idx
            #print(prod_line_tentative.operations[choosen_idx].operation_name)
    
        #random sample of an operation
        
        
        
        #choose the operaiton with the smallest exp_time
        
        
        
        
        if choosen_idx == "forward":
            ocupation_operators.append((20-len(operator_dispo[current_date]))/20)
            echu = prod_line_tentative.forward()
            
            
        else:
            to_plan = prod_line_tentative.operations[choosen_idx]
            
            duration = to_plan.processing_time
            operators_needed = to_plan.operator
            processable_on = to_plan.processable_on
            operator_that_can_operate = to_plan.operator_that_can_operate
            
            
            #compute the available ressources
            for i in range(duration):
                processable_on = list(set(processable_on) & set(machine_dispo[current_date + DateOffset(hours = 12*i)]))
                operator_that_can_operate = list(set(operator_that_can_operate) & set(operator_dispo[current_date + DateOffset(hours = 12*i)]))
                
            #choose the ressources
            machine_to_plan  = sample(processable_on,1)[0]
            operators_to_plan = sample(operator_that_can_operate, operators_needed)
            
            #store the selected ressources

            to_plan.processed_on = machine_to_plan
            
            
            #met a jour les ressources disponibles
            end_date = current_date + DateOffset(hours = 12 * (duration-1))
            if to_plan.operation_name != "IV":
                prod_line_tentative.df_machine.loc[current_date:end_date, machine_to_plan] = operation_machine[to_plan.operation_name, machine_to_plan]
            
            #merge mélangeur et extrudeur
            if machine_to_plan == "m3":
                prod_line_tentative.df_machine.loc[current_date:end_date, "m4"] = operation_machine[to_plan.operation_name, machine_to_plan]
            if machine_to_plan == "m4":
                prod_line_tentative.df_machine.loc[current_date:end_date, "m3"] = operation_machine[to_plan.operation_name, machine_to_plan]
            
            for op in operators_to_plan:
                prod_line_tentative.df_operator.loc[current_date:end_date,op] = to_plan.operation_name
                
                
            #start the operation
            to_plan.status = 1# change the status to en cours
            to_plan.op_begin = current_date
            
            #handle de IV
            if to_plan.operation_name == "IV":
                prod_line_tentative.current_batch_on_IV = to_plan.job_name
            
        if len(echu):
            break
            
        done = prod_line_tentative.check_done()
    
    if not len(echu):
        ocupation_operator_mean.append(ocupation_operators)
        tentatives_prod_line.append(prod_line_tentative)

    


#find the best planning    
no_echu_prod_line_idx = []
min_lead_time = 200
for i,test in enumerate(tentatives_prod_line):
    if test.nbr_echu == 0:
        
        lead_times = test.get_lead_time()
       
        no_echu_prod_line_idx.append(i)
        if np.mean(lead_times) < min_lead_time:
            prod_line = tentatives_prod_line[i]
            min_lead_time = np.mean(lead_times)
            print("with lead_time : ")
            print("min : ", min(lead_times))
            print("max : ", max (lead_times))
            print("mean : ", np.mean(lead_times))
            
        
        



#prepare to visualize
batch_names = prod_line.batch_names



planning_tot_final = pd.DataFrame(columns = ["Job", "Machine", "Operation", "Start", "Duration", "Finish", "op_machine"])
for idx,operation in enumerate(prod_line.operations):
    if operation.operation_name not in ["CAPS", "ENVOI"]:
        data = {"Job" : operation.job_name, 
                "Machine" : operation.processed_on, 
                "Operation" : operation.operation_name, 
                "Start" : operation.op_begin, 
                "Duration" : operation.op_end - operation.op_begin, 
                "Finish" : operation.op_end, 
                "op_machine" : operation_machine[operation.operation_name, operation.processed_on]
                }
        row = pd.DataFrame(data = data,columns = ["Job", "Machine", "Operation", "Start", "Duration", "Finish", "op_machine"], index = [idx])
    
        planning_tot_final = pd.concat([planning_tot_final,row])
    
    

operators = prod_line.df_operator[begin_date:]



machine = prod_line.df_machine[begin_date:]



    
utils.visualize(excel_file, batch_names, planning_tot_final, operators, None)


        
        



