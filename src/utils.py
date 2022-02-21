# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 16:45:59 2021

@author: LDE
"""
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator
import matplotlib as mpl
import json
import random 
import time


def visualize(results ,path = ""):
    
    operation_machine = {
                     (0)   : "QC",
                     (1,1) : "broyage_poly_1",
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
    for index, row in schedule.iterrows():
        
        op = row["Operation"]
        machine = row["Machine"]
        if machine != '0':
            op_machine.append(operation_machine[int(op),int(machine)])
        else:
            op_machine.append(operation_machine[int(machine)])
    
    schedule["op_machine"] = op_machine
    
    jobs = sorted(list(schedule['Job'].unique()))
    operation_machine_sorted = [value for key,value in operation_machine.items()][::-1]
    machines = operation_machine_sorted
    makespan = (schedule['Finish'].max() - schedule['Start'].min()).days
    end_date = schedule['Finish'].max()
    
    
    bar_style = {'alpha':1.0, 'lw':25, 'solid_capstyle':'butt'}
    text_style = {'color':'white', 'weight':'bold', 'ha':'center', 'va':'center'}
    colors = mpl.cm.Dark2.colors

    schedule.sort_values(by=['Job', 'Start'])
    schedule.set_index(['Job', 'op_machine'], inplace=True,append = True)
    
    fig, ax = plt.subplots(2,1, figsize=(12, 5+(len(jobs)+len(machines))/4))
    
    for jdx, j in enumerate(jobs, 1):
        for mdx, m in enumerate(machines, 1):
            for index,_,_ in schedule.index:
                if (index,j,m) in schedule.index:
                    

                    xs = schedule.loc[(index,j,m), 'Start']
                    xf = schedule.loc[(index,j,m), 'Finish']
                    

                    ax[0].plot([xs, xf], [jdx]*2, c=colors[mdx%7], **bar_style)
                    #ax[0].text((xs + xf)/2, jdx, m, **text_style)
                    ax[1].plot([xs, xf], [mdx]*2, c=colors[jdx%7], **bar_style)
                    #ax[1].text((xs + xf)/2, mdx, j, **text_style)
                
    ax[0].set_title('Job Schedule')
    ax[0].set_ylabel('Job')
    ax[1].set_title('Machine Schedule')
    ax[1].set_ylabel('Machine')
    
    for idx, s in enumerate([jobs, machines]):
        ax[idx].set_ylim(0.5, len(s) + 0.5)
        ax[idx].set_yticks(range(1, 1 + len(s)))
        ax[idx].set_yticklabels(s)
        ax[idx].text(end_date, ax[idx].get_ylim()[0], "{0:0.1f}".format(makespan), ha='center', va='bottom')
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
