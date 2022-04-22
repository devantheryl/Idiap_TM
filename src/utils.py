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

def visualize(results ,historical_time, historical_operator, job_stats, path = ""):
    
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
        if machine != '0':
            op_machine.append(operation_machine[int(op),int(machine)])
        else:
            op_machine.append(operation_machine[int(machine)])
    
    schedule["op_machine"] = op_machine
    
    
    jobs = sorted(list(schedule['Job'].unique()))
    operation_machine_sorted = [value for key,value in operation_machine.items()][::-1]
    uniq, index = np.unique(np.array(operation_machine_sorted), return_index=True)
    machines = uniq[index.argsort()]
    schedule = schedule[schedule["op_machine"] != "echu"]
    makespan = (schedule['Start'].max() - schedule['Finish'].min()).days
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
    ax3.step(historical_time,historical_operator, alpha = 1.0, where = 'pre')
    
    
    for idx, s in enumerate([jobs, machines]):
        ax[idx].set_ylim(0.5, 0.5+len(s))
        ax[idx].set_yticks(range(1, 1+len(s)))
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
                return i
            temp = get_new_time(temp,-1)
            i+=1
        
    return 0
    

def generate_test_scenarios(start_date, nbr_job, seed):
    day_stat = [0.3,0.3,0.3,0.1]
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




