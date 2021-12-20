# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 16:45:59 2021

@author: LDE
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import json
import random 
import time


def visualize(results):
    
    operation_machine = {(1,1) : "broyage_poly_1",
                     (1,2) : "broyage_poly_2",
                     (2,3) : "tamisage_poly_3",
                     (3,4) : "mélange_4",
                     (3,5) : "mélange_5",
                     (4,6) : "extrusion_6",
                     (5,1) : "broyage_ug_1",
                     (5,2) : "broyage_ug_2",
                     (6,3) : "tamisage_ug_3",
                     (7,8) : "tween_8",
                     (8,7) : "combinaison_7",
                     (9,9) : "perry_9",
                     (10,10) : "sortie_lyo_10",
                     (11,11) : "capsulage_11",
                     (12,12) : "IV_12",
                     (13,13) : "envoi IRR_13",
                     (14,14) : "retour IRR_14"}
    
    schedule = results.copy()
    
    op_machine = []
    for row in schedule.iterrows():
        
        op = row[1]["Operation"]
        machine = row[1]["Machine"]
        op_machine.append(operation_machine[int(op),int(machine)])
    
    schedule["op_machine"] = op_machine
    
    JOBS = sorted(list(schedule['Job'].unique()))
    operation_machine_sorted = [value for key,value in operation_machine.items()][::-1]
    MACHINES = operation_machine_sorted
    makespan = schedule['Finish'].max()
    
    bar_style = {'alpha':1.0, 'lw':25, 'solid_capstyle':'butt'}
    text_style = {'color':'white', 'weight':'bold', 'ha':'center', 'va':'center'}
    colors = mpl.cm.Dark2.colors

    schedule.sort_values(by=['Job', 'Start'])
    schedule.set_index(['Job', 'op_machine'], inplace=True,append = True)
    
    fig, ax = plt.subplots(2,1, figsize=(12, 5+(len(JOBS)+len(MACHINES))/4))

    for jdx, j in enumerate(JOBS, 1):
        for mdx, m in enumerate(MACHINES, 1):
            for index,_,_ in schedule.index:
                if (index,j,m) in schedule.index:
                    

                    xs = schedule.loc[(index,j,m), 'Start']
                    xf = schedule.loc[(index,j,m), 'Finish']
                    ax[0].plot([xs, xf], [jdx]*2, c=colors[mdx%7], **bar_style)
                    ax[0].text((xs + xf)/2, jdx, m, **text_style)
                    ax[1].plot([xs, xf], [mdx]*2, c=colors[jdx%7], **bar_style)
                    ax[1].text((xs + xf)/2, mdx, j, **text_style)
                
    ax[0].set_title('Job Schedule')
    ax[0].set_ylabel('Job')
    ax[1].set_title('Machine Schedule')
    ax[1].set_ylabel('Machine')
    
    for idx, s in enumerate([JOBS, MACHINES]):
        ax[idx].set_ylim(0.5, len(s) + 0.5)
        ax[idx].set_yticks(range(1, 1 + len(s)))
        ax[idx].set_yticklabels(s)
        ax[idx].text(makespan, ax[idx].get_ylim()[0]-0.2, "{0:0.1f}".format(makespan), ha='center', va='top')
        ax[idx].plot([makespan]*2, ax[idx].get_ylim(), 'r--')
        ax[idx].set_xlabel('Time')
        ax[idx].grid(True)
        
    fig.tight_layout()