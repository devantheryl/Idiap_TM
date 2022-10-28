# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 16:40:36 2022
@author: LDE
"""
from Prod_line_4 import Production_line
import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset



from src.TF_env3 import TF_environment
from tensorforce import Environment, Agent

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

#load the current_date and create the prod_line object
begin_date = pd.to_datetime("2022-10-13", format = "%Y-%m-%d")
prod_line = Production_line(begin_date)



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
    ("MEL_1","m3") : "Mélanges B2 ",
    ("MEL_2","m3") : "Mélanges B2 ",
    
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
    }
operation_raccourci = {
    "Broyage polymère B1" : "BR",
    "Broyage polymère B2" : "BR",
    "Tamisage polymère B2" :"TP",
    "Mélanges B2" : "MEL",
    "Extrusion B2" : "EXT",
    "Broyage bâtonnets B1 " : "BB",
    "Broyage bâtonnets B2 " : "BB",
    "Tamisage Microgranules B2" : "TM",
    "Milieu de suspension  " : "MILIEU",
    "Combin. des fractions de microgranules" : "CF",
    "Sortie Lyo" : "LYO",
    "Capsulage" : "CAPS",
    "Remplissage Poudre + liquide B2" : "LYO"
    
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
    "Remplissage Poudre + liquide B2" : 8
    }

#attribue les opérateurs aux opérations qui n'en ont pas encore 
operators = prod_line.df_operator[begin_date:]
machine = prod_line.df_machine[begin_date:]
operator_stats_df = prod_line.operator_stats_df

for index in machine.index:
    machines_used = machine.loc[index]
    machines_used = machines_used[machines_used!="0"].to_list()
    
    operators_planned = operators.loc[index]
    
    for machine_used in machines_used:
        machine_used_raccourci = operation_raccourci[machine_used]
        test_operator = operators_planned[(machine_used_raccourci == operators_planned) == True].to_list()
        
        #l'opération n'a pas encore d'opérateur attitrés
        if len(test_operator) == 0:
            print(index,machine_used_raccourci, test_operator)
    
    







selected_machines  = {}
done = False
while not done:
    current_date = prod_line.time
    machine_dispo, operator_dispo = prod_line.update_executable()
    
    exectuable_idx = []
    for index, op in enumerate(prod_line.operations):
        if op.executable:
            print(op.operation_name, op.job_name)
            exectuable_idx.append(index)
    
    #si une opération est plannifiable
    if len(exectuable_idx):
        #on en prend une au hasard
        choosen_idx = exectuable_idx[np.random.randint(len(exectuable_idx))]
        to_plan = prod_line.operations[choosen_idx]
        print(to_plan.operation_name, to_plan.job_name)
        duration = to_plan.processing_time
        operators_needed = to_plan.operator
        processable_on = to_plan.processable_on
        operator_that_can_operate = to_plan.operator_that_can_operate
        
        
        #compute the available ressources
        for i in range(duration):
            processable_on = list(set(processable_on) & set(machine_dispo[current_date + DateOffset(hours = 12*i)]))
            operator_that_can_operate = list(set(operator_that_can_operate) & set(operator_dispo[current_date + DateOffset(hours = 12*i)]))
            
        #choose the ressources
        machine_to_plan  = sample(processable_on,1)
        operators_to_plan = sample(operator_that_can_operate, operators_needed)
        
        #store the selected ressources
        selected_machines[choosen_idx] = machine_to_plan[0]
        
        
        #met a jour les ressources disponibles
        end_date = current_date + DateOffset(hours = 12 * (duration-1))
        prod_line.df_machine.loc[current_date:end_date, machine_to_plan] = operation_machine[to_plan.operation_name, machine_to_plan[0]]
        for op in operators_to_plan:
            prod_line.df_operator.loc[current_date:end_date,op] = to_plan.operation_name
            
            
        #start the operation
        to_plan.status = 1# change the status to en cours
        to_plan.op_begin = current_date
        
        
    else:
        print(prod_line.forward())
        
    done = prod_line.check_done()
    
#prepare to visualize
batch_names = prod_line.batch_names





planning_tot_final = pd.DataFrame(columns = ["Job", "Machine", "Operation", "Start", "Duration", "Finish", "op_machine"])
for idx,(key, _) in enumerate(selected_machines.items()):
    machine = selected_machines[key]
    
    operation = prod_line.operations[key]
    
    data = {"Job" : operation.job_name, 
            "Machine" : machine, 
            "Operation" : operation.operation_name, 
            "Start" : operation.op_begin, 
            "Duration" : operation.op_end - operation.op_begin, 
            "Finish" : operation.op_end, 
            "op_machine" : operation_machine[operation.operation_name, machine]
            }
    row = pd.DataFrame(data = data,columns = ["Job", "Machine", "Operation", "Start", "Duration", "Finish", "op_machine"], index = [idx])

    planning_tot_final = pd.concat([planning_tot_final,row])
    
    

operators = prod_line.df_operator[begin_date:]



machine = prod_line.df_machine[begin_date:]



    
utils.visualize("data/Planning_Production 2022_13.10.2022.xlsm", batch_names, planning_tot_final, operators, None)


        
        



