# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 15:03:28 2022

@author: LDE
"""

import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset



from src.TF_env3 import TF_environment
from tensorforce import Environment, Agent

import src.utils as utils



import place_operator as utils_operators
import place_operations as utils_operations

import operator_stats as op_stats



operations_driver = {
    "Broyage polymère B1" : "BR",
    "Broyage polymère B2" : "BR",
    "Tamisage polymère B2" : "TP",
    "Mélanges B1 " : "MEL",
    "Extrusion B1" : "EX",
    "Mélanges B2" : "MEL",
    "Extrusion B2" : "EX",
    "Broyage bâtonnets B1 " : "BB" ,
    "Broyage bâtonnets B2 " : "BB",
    "Tamisage Microgranules B2" : "TM",
    "Combin. des fractions de microgranules" : "CF",
    "Milieu de suspension  " : "MILIEU",
    "Remplissage Poudre + liquide B2" : "PERRY",
    "Sortie Lyo" : "SORTIELYO",
    "Capsulage" : "CAPS",
    "Inspection visuelle " : "IV",
    "Inspection visuelle automatique " : "IV",
    "Inspection visuelle" : "IV",
    }


def get_batch_to_plan(df, date):

    ressources = df.loc[date:]
    
    """
    find all the batches that have the Perry planned from current_date
    """
    next_batches = np.empty((0,7))
    for index, row in ressources.loc[:,"Remplissage Poudre + liquide B2"].iterrows():
        batch_number = row["N° de dossier"]
        if "ROD-" in batch_number:
            #to resolve the issue when it's written ROD instead of PROD
            if batch_number[:4] == "ROD-":
                batch_number = "P" + batch_number
                
            if "3.75" in batch_number:
                formulation = 1
            if "11.25" in batch_number:
                formulation = 3
            if "22.5" in batch_number:
                formulation = 6
            if batch_number not in next_batches:
                date = index
                fraction = row["Remarque"]
                fraction = fraction.replace(" ", "")
                
                    
                scale = str(row["Echelle"])
                scale = scale.replace("'","").replace(" ", "")
                if "/" in scale:
                    scale = scale.split("/")[1]
                    
                if "22.5" in batch_number:
                    next_batches = np.append(next_batches,[[batch_number,date,"fraction1",formulation ,scale,0 ,False]],axis = 0)
                    next_batches = np.append(next_batches,[[batch_number,date,"fraction2",formulation ,scale,0 ,False]],axis = 0)
                else:
                    next_batches = np.append(next_batches,[[batch_number,date,fraction,formulation ,scale,0 ,False]],axis = 0)
                
    
    """
    find the mel-ex PF for all batches if any
    """
    BB = df.columns.levels[0][8:10] #get the 2 broyage ug columns
    for index, batches in enumerate(next_batches[:,0]):
        for column in BB:
            try:
                rows        = df.loc[:,column]
                rows        = rows.loc[rows["N° de dossier"].str.contains(batches)]
                pf          = rows.iloc[0]["N° PF Mel-Ex"]
                fraction    = rows.iloc[0]["Fraction"]
                
                #the pf can be either in PF or fraction (excel is not normalized)
                if "PF-" in pf:
                    next_batches[index,5] = pf
                if "PF-" in fraction:
                    next_batches[index,5] = fraction[:15]
                
            except:
                pass
    
    """
    attribute all the operation for all batches
    """
    batches_dict = {}
    for index, batches in enumerate(next_batches[:,0]):
        
        formulation = next_batches[index,3]
        fraction = next_batches[index,2]
        
        if formulation == 6 and fraction == "fraction1":
            batches_dict[batches+"_1"] = []
        if formulation == 6 and fraction == "fraction2":
            batches_dict[batches+"_2"] = []
        if formulation == 1 or formulation == 3:
            batches_dict[batches] = []
        
        for column in df.columns.levels[0]:
            try:
                rows = df.loc[:,column]
                rows = rows.loc[rows["N° de dossier"].str.contains(batches)]
                if formulation ==6 and fraction == "fraction1":
                    try:
                        rows_fraction = rows.loc[rows["N° de dossier"].str.contains("75:25") == False]
                        if len(rows_fraction):
                            batches_dict[batches + "_1"].append((operations_driver[column],rows_fraction.index.tolist(),column))
                            
                    except:
                        pass
                if formulation ==6 and fraction == "fraction2":
                     try:
                         rows_fraction = rows.loc[rows["N° de dossier"].str.contains("75:25")]
                         if len(rows_fraction):
                             batches_dict[batches + "_2"].append((operations_driver[column],rows_fraction.index.tolist(),column))
                     except:
                         pass
                if formulation == 1 or formulation == 3:
                    if len(rows):
                        batches_dict[batches].append((operations_driver[column],rows.index.tolist(),column))
                        
            except:
                pass
    
    """
    check wether the batch is finished or not
    """
    formu1_1_scale6600 = ["BR", "TP", "MEL", "EX", "BB", "TM", "MILIEU", "PERRY", "CAPS"]
    formu1_2_scale6600 = ["BB", "TM", "MILIEU", "PERRY", "CAPS"]
    formu1_scale20000 = ["BR", "TP", "MEL", "EX", "BB", "TM", "MILIEU", "PERRY", "CAPS"]
    formu3_1_scale6600 = ["BR", "TP", "MEL", "EX", "BB", "TM", "MILIEU", "PERRY", "CAPS"]
    formu3_2_scale6600 = ["BB", "TM", "MILIEU", "PERRY", "CAPS"]
    formu3_scale20000 =["BR", "TP", "MEL", "EX", "BB", "TM", "MILIEU", "PERRY", "CAPS"]
    formu6_1_scale20000 = ["BR", "TP", "MEL", "EX", "BB", "TM", "MILIEU","CF", "PERRY", "CAPS"]
    formu6_2_scale20000 = ["BR", "TP", "MEL", "EX", "BB", "TM"]
    operation_to_plan = {}
    for index, batches in enumerate(next_batches[:,0]):
        
        scale = next_batches[index,4]
        formulation = next_batches[index,3]
        split = next_batches[index,2]
        date_perry = next_batches[index,1]
        operation_to_plan[batches] = []
        
        if formulation == 6:
            fraction1 = batches_dict[batches+"_1"]
            fraction2 = batches_dict[batches+"_2"]
            for required in formu6_1_scale20000:
                operation_done = False
                date_op_begin = None
                date_op_end = None
                machine = None
                for operation_planned in fraction1:
                    if required in operation_planned[0]:
                        operation_done = True
                        date_op_begin = operation_planned[1][0]
                        date_op_end = operation_planned[1][-1]
                        machine = operation_planned[2]
                        
                
                operation_to_plan[batches].append((required,formulation,"fraction1",20000,date_perry,date_op_begin,date_op_end,operation_done,machine))
                
            for required in formu6_2_scale20000:
                operation_done = False
                date_op_begin = None
                date_op_end = None
                machine = None
                
                for operation_planned in fraction2:
                    if required in operation_planned[0]:
                        operation_done = True
                        date_op_begin = operation_planned[1][0]
                        date_op_end = operation_planned[1][-1]
                        machine = operation_planned[2]
                        
                operation_to_plan[batches].append((required,formulation,"fraction2",20000,date_perry,date_op_begin,date_op_end,operation_done,machine))
                    
        if formulation == 3 and "6600" in scale:
            fraction = batches_dict[batches]
            if "fraction1" in split:
                for required in formu3_1_scale6600:
                    operation_done = False
                    date_op_begin = None
                    date_op_end = None
                    machine = None
                    for operation_planned in fraction:
                        if required in operation_planned[0]:
                            operation_done = True
                            date_op_begin = operation_planned[1][0]
                            date_op_end = operation_planned[1][-1]
                            machine = operation_planned[2]
                    
                    operation_to_plan[batches].append((required,formulation,split,6600,date_perry,date_op_begin,date_op_end,operation_done,machine))
                    
            if "fraction2" in split:
                for required in formu3_2_scale6600:
                    operation_done = False
                    date_op_begin = None
                    date_op_end = None
                    machine = None
                    for operation_planned in fraction:
                        if required in operation_planned[0]:
                            operation_done = True
                            date_op_begin = operation_planned[1][0]
                            date_op_end = operation_planned[1][-1]
                            machine = operation_planned[2]
                    
                    operation_to_plan[batches].append((required,formulation,split,6600,date_perry,date_op_begin,date_op_end,operation_done,machine))
    
        if formulation == 3 and "20000" in scale:
            fraction = batches_dict[batches]
            for required in formu3_scale20000:
                operation_done = False
                date_op_begin = None
                date_op_end = None
                machine = None
                for operation_planned in fraction:
                    if required in operation_planned[0]:
                        operation_done = True
                        date_op_begin = operation_planned[1][0]
                        date_op_end = operation_planned[1][-1]
                        machine = operation_planned[2]
                
                operation_to_plan[batches].append((required,formulation,split,20000,date_perry,date_op_begin,date_op_end,operation_done,machine))
                    
        if formulation == 1 and "6600" in scale:
            fraction = batches_dict[batches]
            if "fraction1" in split:
                for required in formu1_1_scale6600:
                    operation_done = False
                    date_op_begin = None
                    date_op_end = None
                    machine = None
                    for operation_planned in fraction:
                        if required in operation_planned[0]:
                            operation_done = True
                            date_op_begin = operation_planned[1][0]
                            date_op_end = operation_planned[1][-1]
                            machine = operation_planned[2]
                    
                    operation_to_plan[batches].append((required,formulation,split,6600,date_perry,date_op_begin,date_op_end,operation_done,machine))
            if "fraction2" in split:
                for required in formu1_2_scale6600:
                    operation_done = False
                    date_op_begin = None
                    date_op_end = None
                    machine = None
                    for operation_planned in fraction:
                        if required in operation_planned[0]:
                            operation_done = True
                            date_op_begin = operation_planned[1][0]
                            date_op_end = operation_planned[1][-1]
                            machine = operation_planned[2]
                    
                    operation_to_plan[batches].append((required,formulation,split,6600,date_perry,date_op_begin,date_op_end,operation_done,machine))
    
        if formulation == 1 and "20000" in scale:
            fraction = batches_dict[batches]
            for required in formu1_scale20000:
                operation_done = False
                date_op_begin = None
                date_op_end = None
                machine = None
                for operation_planned in fraction:
                    if required in operation_planned[0]:
                        operation_done = True
                        date_op_begin = operation_planned[1][0]
                        date_op_end = operation_planned[1][-1]
                        machine = operation_planned[2]
                
                operation_to_plan[batches].append((required,formulation,split,20000,date_perry,date_op_begin,date_op_end,operation_done,machine))
            
    for key, value in operation_to_plan.copy().items():
        batch_done = True
        for op in value:
            if op[-2] == False:
                batch_done = False
        if batch_done:
            del operation_to_plan[key]
                
    
    
    
    return operation_to_plan
                
        
            



def get_operations_graph(operation_to_plan):
    """
    create a list of vertices representing all operation
    """
    vertices = []
    
    #vertices = pd.DataFrame(columns = ["batch", "op", "formulation", "fraction", "scale", "op_date", "perry_date", "done"],index=np.arange(nbr_operations))
    for key, value in operation_to_plan.items():
        for op in value:
            vertices.append((key,op))
    nbr_operations = len(vertices)
            
    """
    create adjacency list to connect operatons in the same batch and the fraction of one batch to the other fraction
    """
    
    adjacency = np.zeros((nbr_operations,nbr_operations))
    for i in range(nbr_operations):
        op_ref = vertices[i][1]
        batch_ref = vertices[i][0]
        for j in range(nbr_operations):
            op_prob = vertices[j][1]
            batch_prob = vertices[j][0]
            
            #if the batches are the same 
            if batch_ref == batch_prob:
                #if the operations are not the same 
                if op_ref[0] != op_prob[0]:
                    #connect millieu et perry if same fraction
                    if op_ref[0] == "MILIEU" and op_prob[0] == "PERRY" and op_ref[2] == op_prob[2]:
                        adjacency[i,j] = 1
                        
                    if op_ref[0] == "CF" and op_prob[0] == "PERRY":
                        adjacency[i,j] = 1
                        
                    if op_ref[0] == "BR" and op_prob[0] == "TP" and op_ref[2] == op_prob[2]:
                        adjacency[i,j] = 1
                        
                    if op_ref[0] == "TP" and op_prob[0] == "MEL" and op_ref[2] == op_prob[2]:
                        adjacency[i,j] = 1
                    
                    if op_ref[0] == "MEL" and op_prob[0] == "EX" and op_ref[2] == op_prob[2]:
                        adjacency[i,j] = 1
                    
                    if op_ref[0] == "EX" and op_prob[0] == "BB" and op_ref[2] == op_prob[2]:
                        adjacency[i,j] = 1
                        
                    if op_ref[0] == "BB" and op_prob[0] == "TM" and op_ref[2] == op_prob[2]:
                        adjacency[i,j] = 1
                        
                    if op_ref[0] == "TM" and op_prob[0] == "PERRY" and (op_ref[1] == 1 or op_ref[1] == 3):
                        adjacency[i,j] = 1
                        
                    if op_ref[0] == "TM" and op_prob[0] == "CF" and op_ref[1] == 6:
                        adjacency[i,j] = 1
                        
                    if op_ref[0] == "PERRY" and op_prob[0] == "CAPS":
                        adjacency[i,j] = 1
            
            #inter batch connexion
            if batch_ref[:-2] == batch_prob[:-2]:
                
                if op_ref[0] == "EX" and op_prob[0] == "BB" and op_ref[2] == "fraction1" and op_prob[2] == "fraction2" and (int(batch_ref[-2:])+1) == int(batch_prob[-2:]):
                    adjacency[i,j] = 1
                
    return vertices, adjacency




def get_operators_for_operations(vertices, operator_stats_df):
    """
    get the operator that can operate each operation
    """
    operator_that_can_operate = {}
    for index,op in enumerate(vertices):
        op = op[1][0]
        
        operator_that_can_operate[index] = operator_stats_df.loc[op][operator_stats_df.loc[op] == 1].index.tolist()
        
    return operator_that_can_operate


   





    