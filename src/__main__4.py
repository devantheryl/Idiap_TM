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



selected_operators = {}
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
        selected_operators[choosen_idx] = operators_to_plan
        
        
        #met a jour les ressources disponibles
        end_date = current_date + DateOffset(hours = 12 * (duration-1))
        prod_line.df_machine.loc[current_date:end_date, machine_to_plan] = 1
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
                     
                     ("MEL","m3") : "Mélanges B1 ",
                     ("MEL_1","m3") : "Mélanges B1 ",
                     ("MEL_2","m3") : "Mélanges B1 ",
                     
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


final_selected_operators = {}
planning_tot_final = pd.DataFrame(columns = ["Job", "Machine", "Operation", "Start", "Duration", "Finish", "op_machine"])
for idx,(key, _) in enumerate(selected_machines.items()):
    machine = selected_machines[key]
    operators = selected_operators[key]
    
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
    final_selected_operators[idx] = operators
    
    planning_tot_final = pd.concat([planning_tot_final,row])
    
    
    
    
operator_excel_rows = {
        "SFR" : 192, 
        "BPI" : 194, 
        "JPI" : 196, 
        "JDD" : 198, 
        "FDS" : 200, 
        "SFH" : 202, 
        "NDE" : 204, 
        "LTF" : 206, 
        "SRG" : 208, 
        "JPE" : 210, 
        "RPI" : 212, 
        "ANA" : 214,
        "MTR" : 216, 
        "CMT" : 218, 
        "CGR" : 220, 
        "CPO" : 222, 
        "REA" : 224,
        "NRO" : 227,
        "VZU" : 229,
        "ACH" : 231,
        "LBU" : 233
    }

operators = prod_line.df_operator[begin_date:]
test = operators.loc[begin_date:begin_date + DateOffset(hours = 12)].T
test = test.rename(index=operator_excel_rows)


excel_cell_operators = ["A" + str(index_operator) for index_operator in test.index.to_list()]
occ1 = test.T.iloc[0].to_list()[0]
occ2 = test.T.iloc[1].to_list()





    
utils.visualize("data/Planning_Production 2022_13.10.2022.xlsm", batch_names, planning_tot_final, operators, None)


        
        



