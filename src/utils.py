# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 16:45:59 2021

@author: LDE
"""
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator
import matplotlib.patches as pat
import matplotlib as mpl
import json
import random 
import time
from datetime import datetime, timedelta, date
import matplotlib.dates as mdates
import numpy as np
import xlwings as xw
from openpyxl import load_workbook
import openpyxl
from openpyxl.utils import range_boundaries
from openpyxl.utils.cell import get_column_letter
from itertools import islice
import pandas as pd
from unidecode import unidecode

def visualize(results ,historical_time, historical_operator, path = ""):
    
    operation_machine = {
                     (0) : "echu",
                     (1,1) : "broyage_poly_1",
                     (1,2) : "broyage_poly_2",
                     (2,1) : "broyage_poly_1",
                     (2,2) : "broyage_poly_2",
                     (3,3) : "tamisage_poly_3",
                     (4,3) : "tamisage_poly_3",
                     (5,4) : "mélange_4",
                     (6,4) : "mélange_4",
                     (7,5) : "extrusion_6",
                     (8,5) : "extrusion_6",
                     (9,1) : "broyage_ug_1",
                     (9,2) : "broyage_ug_2",
                     (10,1) : "broyage_ug_1",
                     (10,2) : "broyage_ug_2",
                     (11,3) : "tamisage_ug_3",
                     (12,3) : "tamisage_ug_3",
                     (13,7) : "tween_8",
                     (14,6) : "combinaison_7",
                     (15,8) : "perry_9",
                     (16,9) : "sortie_lyo_10",
                     (17,10) : "capsulage_11",
                     (18,11) : "IV_12",
                     (19,12) : "envoi IRR_13",
                     (20,13) : "retour IRR_14"
    }
    
    schedule = results.copy()
    
    
    
    op_machine = []
    for index, row in schedule.iterrows():
        
        op = row["Operation"]
        machine = row["Machine"]
        duration = row["Duration"]
        if duration != 0:
            op_machine.append(operation_machine[int(op),int(machine)])
        else:
            op_machine.append(operation_machine[0])
    
    schedule["op_machine"] = op_machine
    
    
    jobs = sorted(list(schedule['Job'].unique()))
    operation_machine_sorted = [value for key,value in operation_machine.items()][::-1]
    uniq, index = np.unique(np.array(operation_machine_sorted), return_index=True)
    machines = uniq[index.argsort()]
    schedule = schedule[schedule["op_machine"] != "echu"]
    #makespan = (schedule['Start'].max() - schedule['Finish'].min()).days
    end_date = schedule['Finish'].max()
    
    
    bar_style = {'alpha':1.0, 'lw':25, 'solid_capstyle':'butt'}
    text_style = {'color':'white', 'weight':'bold', 'ha':'center', 'va':'center'}
    colors = mpl.cm.Dark2.colors

    schedule.sort_values(by=['Job', 'Start'])
    schedule.set_index(['Job', 'op_machine'], inplace=True,append = True)
    
    fig, ax = plt.subplots(2,1, figsize=(30, (len(jobs)+len(machines))))
    
    for jdx, j in enumerate(jobs, 1):
        for mdx, m in enumerate(machines, 1):
            for index,_,_ in schedule.index:
                if (index,j,m) in schedule.index:
                    
                    
                    xs = schedule.loc[(index,j,m), 'Start']
                    xf = schedule.loc[(index,j,m), 'Finish']
                    xs = mdates.date2num(xs)
                    xf = mdates.date2num(xf)
                    width = xf-xs
                    
                    op = schedule.loc[(index,j,m), 'Operation']
                    
                        
                    ax[0].plot([xs, xf], [jdx]*2, c=colors[mdx%7], **bar_style)
                    #ax[0].text((xs + xf)/2, jdx, m, **text_style)
                    
                    if op in [1,3,5,7,9,11]:
                        rect = pat.Rectangle((xs, mdx-0.5), width, 1, linewidth=2,facecolor=colors[jdx%7], linestyle = 'solid', ec = "black")
                        
                        #ax[1].plot([xs, xf], [mdx]*2, c=colors[jdx%7], **bar_style, linestyle='dashed')
                        ax[1].add_patch(rect)
                    else:
                        #ax[1].plot([xs, xf], [mdx]*2, c=colors[jdx%7], **bar_style, linestyle='dotted')
                        rect = pat.Rectangle((xs, mdx-0.5), width, 1, linewidth=2, facecolor=colors[jdx%7], linestyle = 'dotted',ec = "black")
                        ax[1].add_patch(rect)
                    #ax[1].text(xs, mdx, j, **text_style)
                    
                        
                
    ax[0].set_title('Job Schedule')
    ax[0].set_ylabel('Job')
    ax[1].set_title('Machine Schedule')
    ax[1].set_ylabel('Machine')
    
    ax3 = ax[1].twinx()
    ax3.set_ylabel("operator")
    ax3.step(historical_time,historical_operator, alpha = 1.0, where = 'post')
    
    
    for idx, s in enumerate([jobs, machines]):
        ax[idx].set_ylim(0.5, 0.5+len(s))
        ax[idx].set_yticks(range(1, 1+len(s)))
        ax[idx].set_yticklabels(s)
        #ax[idx].text(end_date, ax[idx].get_ylim()[0], "{0:0.1f}".format(makespan), ha='center', va='bottom')
        ax[idx].plot([end_date]*2, ax[idx].get_ylim(), 'r--')
        ax[idx].set_xlabel('Time')
        ax[idx].grid(True)
        ax[idx].xaxis.set_major_locator(DayLocator())
        
    
        
    fig.tight_layout()
    fig.autofmt_xdate()
    #fig.show()
    
    if len(path):
        fig.savefig(path)
    fig.savefig("test.png")
    
    

def get_new_time(current_time, delta):
    temp = current_time
    
    for i in range(abs(delta)):
        if delta < 0:
            if temp.time().hour == 12:
                temp -= timedelta(hours = 12)
            else:
                temp -= timedelta(days=1)
                temp = temp.replace(hour = 12)
        else :
            if temp.time().hour == 00:
                temp += timedelta(hours = 12)
            else:
                temp += timedelta(days=1)
                temp = temp.replace(hour = 00)
            pass
    return temp


def get_delta_time(current_time, target_time):
    
    
    if current_time > target_time:
        temp = current_time
        i = 0
        while(1):
            if temp == target_time:
                return i
            temp = get_new_time(temp,-1)
            i +=1
    
    if current_time < target_time:
        i = 0
        temp = target_time
        while(1):
            if temp == current_time:
                return -i
            temp = get_new_time(temp,-1)
            i+=1
        
    return 0
    

def generate_test_scenarios(start_date, nbr_job, seed):
    day_stat = [0.25,0.25,0.25,0.25]
    formu_stat = [0.25,0.25,0.5]
    
    target_dates = {}
    start_date = datetime.fromisoformat(start_date)
    np.random.seed(seed)
    i=0
    while i < nbr_job:
        day = np.random.choice([0,1,2,3], 1, p = day_stat)[0]
        
        #if jeudi
        if day == 3:
            formu = np.random.choice([1,3,6], 1, p = formu_stat)[0]
            target_dates[str(start_date)] = formu #on ajoute aussi le lundi
            if i+1<nbr_job:
                i += 1
            else:
                return target_dates
            
        formu = np.random.choice([1,3,6], 1, p = formu_stat)[0]
        target_date = get_new_time(start_date, 2*day)
        target_dates[str(target_date)] = formu
        start_date = get_new_time(start_date, 14) # + 1 week
        
        i +=1
        
    return target_dates


def unmerge_excel(excel_file):
    #load the plannign
    wb = load_workbook(filename = excel_file ,data_only = True, keep_vba = True)
    ws = wb["PLANNING"]
    
    #unmerge the cell in the file
    mergedcells =[]  
    for group in ws.merged_cells.ranges:
        mergedcells.append(group)
    
    for group in mergedcells:
        min_col, min_row, max_col, max_row = group.bounds 
        top_left_cell_value = ws.cell(row=min_row, column=min_col).value
        ws.unmerge_cells(str(group))   # you need to unmerge before writing (see explanation #1 below)
        for irow in range(min_row, max_row+1):
            for jcol in range(min_col, max_col+1): 
                ws.cell(row = irow, column = jcol, value = top_left_cell_value)
                
    #now "ws" is the excel file unmerged
    #convert openpyxl format to pandas
    data = ws.values
    cols = next(data)[1:]
    data = list(data)
    idx = [r[0] for r in data]
    data = (islice(r, 1, None) for r in data)
    df = pd.DataFrame(data, index=idx, columns=cols)
    
    #keep only machines and operator index
    df = df[~df.index.duplicated(keep='first')]
    index_to_keep = df.index.dropna()
    
    df = df.loc[index_to_keep]
    
    df =df.drop(df.filter(like='None').columns, axis=1)
    df = df.drop(columns = df.columns[0])
    
    #resample the column of df
    columns = pd.to_datetime(df.columns)
    
    resampled_date = pd.DataFrame(0,columns=[""],index=columns).resample('12H', closed = "left").mean().index.tolist()
    df = df.iloc[: , :-1] #drop the last column to make the datetime list fit
    df.columns = resampled_date
    df_t = df.transpose() #transpose to have the date as index
    df_t = df_t.drop(columns = df_t.columns[0])#again drop useless column
    df_t = df_t.fillna('0')
    
    return df_t

def extract_machine_operator_state(df):
    
    #extract_machine
    machines = ['Broyage polymère B1', 'Broyage polymère B2', 'Tamisage polymère B2',
           'Mélanges B1 ', 'Extrusion B1', 'Mélanges B2', 'Extrusion B2',
           'Broyage bâtonnets B1 ', 'Broyage bâtonnets B2 ',
           'Tamisage Microgranules B2', 'Combin. des fractions de microgranules',
           'Milieu de suspension  ', 'Remplissage Poudre + liquide B2', 'Sortie Lyo','Capsulage']
    
    operators = ["SFR", "BPI", "JPI", "JDD", "FDS", "SFH", "NDE", "LTF", "SRG", "JPE", "RPI", "ANA",
                "MTR", "CMT", "CGR", "CPO", "REA", "LBU"]
    
    
    merge_occupations = ["OCTODURE", "BP", "TP", "MEL", "EXT",  "BB", "TM", "CF", "MILIEU", 
                     "LYO", "CAPS", "IV", "LAVERIE", "FORMATION", "ETIQUE", 
                     "REQUALIF", "NETTOYAGE", "TEST", "VACANCE", "ABSENT" ,"CONGE",]
    
    vacances_occupations = ["VACANCE", "ABSENT" ,"CONGE","FORMATION", "IV"]
    
    machine_dict = {"m1" : ['Broyage polymère B1','Broyage bâtonnets B1 ' ],
                    "m2" : ['Broyage polymère B2','Broyage bâtonnets B2 '],
                    "m3" : ['Tamisage polymère B2', 'Tamisage Microgranules B2'],
                    "m4" : ['Mélanges B1 ', 'Mélanges B2'],
                    "m5" : ['Extrusion B1','Extrusion B2'],
                    "m6" : ['Combin. des fractions de microgranules'],
                    "m7" : ['Milieu de suspension  '],
                    "m8" : ['Remplissage Poudre + liquide B2'],
                    "m9" : ['Sortie Lyo'],
                    "m10": ['Capsulage']
                    
                    }
    
    vacances_conge2022 = ["2022-04-18","2022-05-26","2022-05-27", "2022-06-06","2022-06-16", "2022-08-01", "2022-08-15",
                          "2022-11-01", "2022-12-08", "2022-12-26","2022-12-27", "2022-12-28", "2022-12-29", "2022-12-30"]
    
    operator_machine_dict = {"m1" : 2,
                             "m2" : 2,
                             "m3" : 2,
                             "m4" : 3,
                             "m5" : 2,
                             "m6" : 2,
                             "m7" : 2,
                             "m8" : 8,
                             "m9" : 2,
                             "m10": 2,
                             }
    
    columns_name = df.columns
    df_machine = df[machines].copy()
    
    #merge same step using the same machine
    column_to_use = ["operator", "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8"]
    df_machine["operator"] = 17
    
    
    #EXTRAIT L'UTILISATION DES MACHINES + LES OPERATEURS UTILISé PAR LES OPERATIONS PLANNIFIéES
    for key, value in machine_dict.items():
        df_machine[key] = "0"
        df_machine[key + "_operator"] = "0"
        
        for machine in value:
            
            #machine utilisée si la case != '0'
            df_machine.loc[df_machine[machine] != "0", key] = "1" 
            
            #operator utilisé uniquement si la case contient un 'PROD'$
            df_machine.loc[df_machine[machine].str.contains("PROD"),key + "_operator"] = "1"
            
        df_machine[key] = df_machine[key].astype(int)
        df_machine[key + "_operator"] = df_machine[key + "_operator"].astype(int)
        
        df_machine["operator"] = df_machine["operator"] - df_machine[key + "_operator"] * operator_machine_dict[key]
        
        
    df_ressources_final = df_machine[column_to_use]
    
    
    #EXTRAIT LES TACHE EFFECTUéE PAR LES OPéRATEURS
    df_operator = df[operators].copy()
    
    #normalise les noms des occupations
    for operator in operators:
        df_operator[operator] = df_operator[operator].apply(unidecode).str.upper()
        for potential in merge_occupations:
            df_operator.loc[df_operator[operator].str.contains(potential),operator] = potential
            
    #extrait les vacances congé, formation et IV, update le nombre d'operator
    for row in df_operator.iterrows():
        row_index = row[0]

        
        for operator in operators:
            if row[1][operator] in vacances_occupations:
                df_ressources_final.loc[row_index,"operator"] = df_ressources_final.loc[row_index,"operator"] - 1
                
        #met à 0 les operators pour les jour de congé
        row_index_str = row_index.strftime("%Y-%m-%d")
        if row_index_str in vacances_conge2022 or row_index.weekday() >4:
            df_ressources_final.loc[row_index,"operator"] = 0
        else:
            #enlève 2 operator pour la laverie et 2 pour octodure
            df_ressources_final.loc[row_index,"operator"] = df_ressources_final.loc[row_index,"operator"] - 4
        
        
    
    return df_ressources_final, df_operator




