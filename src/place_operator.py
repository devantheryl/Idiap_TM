# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 16:15:42 2022

@author: LDE
"""
import pandas as pd

def place_operator(df_operator, planning):
        
    operators = ["SFR", "BPI", "JPI", "JDD", "FDS", "SFH", "NDE", "LTF", "SRG", "JPE", "RPI", "ANA",
                "MTR", "CMT", "CGR", "CPO", "REA"]
    
    operators_stats = pd.read_csv("C:/Users/LDE/Prog/projet_master/digital_twins/data/operator_stats.csv", delimiter =  ";", index_col = 0)
    
    operation_occupations = {
        "Broyage polymère B1": "BP",
        "Broyage polymère B2" : "BP",
        "Tamisage polymère B2" : "TP",          
        "Mélanges B1 " : "MEL",
        "Extrusion B2" : "EXT",
        "Broyage bâtonnets B1 " : "BB",
        "Broyage bâtonnets B2 " : "BB",
        "Tamisage Microgranules B2" : "TM",
        "Milieu de suspension  " : "MILIEU",
        "Combin. des fractions de microgranules" : "CF",
        "Remplissage Poudre + liquide B2" : "LYO",
    }
    
    operator_needed = {
        "BP" : 2,
        "TP" : 2,
        "MEL" : 3,
        "EXT" : 2,
        "BB" : 2,
        "TM" : 2,
        "MILIEU" : 2,
        "CF" : 2,
        "LYO" : 8
    }
    
    #ajoute les occupations octodure et laverie au planning 
    date_min = planning["Start"].min()
    date_max = planning["Finish"].max()

    date_index = pd.date_range(start = date_min, end = date_max, freq = "12H")# 1D car octo et laverie dure toujours 1D, avec les meme opérateurs
    
    for i in range(0,len(date_index)-1,2):
        row_operator = df_operator.loc[date_index[i]]
        nbr_octodure = 0
        nbr_laverie = 0
        for operator in operators:
            if row_operator[operator] == "OCTODURE":
                nbr_octodure += 1
            if row_operator[operator] == "NETTOYAGE":
                nbr_laverie += 1
            pass
        
        if nbr_octodure <2:
            pass
            
        if nbr_laverie <2:
            pass
    
    selected_operators = {}
    for row_operation in planning.iterrows():
        start = row_operation[1]["Start"]
        finish = row_operation[1]["Finish"]
        operation = operation_occupations[row_operation[1]["op_machine"]]
        
        qualified_operators = operators_stats.loc[operation][operators_stats.loc[operation] >0]
        
        df_operator_operation = df_operator.loc[start:finish]
        
        free_operator = df_operator_operation == "0"
        free_operator = free_operator.loc[:,free_operator.all()].columns
        
        
        free_qualified_operator = []
        for free_op in free_operator:
            if free_op in qualified_operators.index.to_list():
                free_qualified_operator.append(free_op)
                
            
        free_qualified_operator = qualified_operators.loc[free_qualified_operator]
        
        
        selected_operators[row_operation[0]] = free_qualified_operator.sample(n = operator_needed[operation], weights =free_qualified_operator.to_list()).index.to_list()
        
        for op in selected_operators[row_operation[0]]:
            df_operator.loc[start:finish, op] = operation
        
        
        
        
    return selected_operators
    
    
        
    
    
    