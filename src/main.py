import numpy as np
import pandas as pd 
from importlib import reload
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
from importlib import reload
import matplotlib.pyplot as plt
import matplotlib as mpl
import json
import random 
import time
from collections import deque

from src.Machine2 import Machine
from src.Job2 import Job
from src.Operation2 import Operation
from src.Agent2 import Agent
from src.Production_line2 import Production_line

import matplotlib.pyplot as plt


from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Dense, Embedding, Reshape
from tensorflow.keras.optimizers import Adam



nbr_job_max = 1
nbr_operation_max = 14
nbr_machines = 14
nbr_operator = 12


batch_size = 32

n_episode = 10000
UPDATE_FREQ = 8
NETW_UPDATE_FREQ = 50
loop_number = 0


prod_line = Production_line(nbr_job_max, nbr_operation_max, nbr_machines, nbr_operator)
job1 = Job("TEST1", 1,20000, nbr_operation_max)
job2 = Job("TEST2", 1,20000, nbr_operation_max)
job3 = Job("TEST3", 1,20000, nbr_operation_max)

prod_line.add_job(job1)
prod_line.add_job(job2)
prod_line.add_job(job3)

agent = Agent(prod_line.state_size, len(prod_line.actions_space))
score_mean = deque(maxlen = 100)
to_plot = []

start = time.time()


actions_space = prod_line.actions_space
for e in range(n_episode):
    prod_line = Production_line(nbr_job_max, nbr_operation_max, nbr_machines, nbr_operator)
    job1 = Job("TEST1", 1,20000, nbr_operation_max)
    prod_line.add_job(job1)
    
    state = prod_line.get_state()
    done = False
    score = 0
    
    while not done:
        mask = prod_line.get_mask()
        action = agent.act(state,mask)
        next_state, reward, done = prod_line.step(action)
        
        agent.remember(state, action, reward, next_state, done)
        
        state = next_state
            
        score += reward
        
        
        if loop_number % UPDATE_FREQ == 0 and loop_number > batch_size:
            agent.replay(batch_size)
            pass
            
        if loop_number % NETW_UPDATE_FREQ == 0:
            
            agent.alighn_target_model()
            
        loop_number += 1
        if done:
            print("episode : {}/{}, score : {}, e : {:.2}".format(e, n_episode, score, agent.epsilon))
            score_mean.append(score)
            break
            
    print("score mean over 100 episode : " ,np.mean(score_mean))
    to_plot.append(np.mean(score_mean))

print('It took', (time.time()-start)/n_episode, 'seconds.')
plt.plot(to_plot)



agent.set_test_mode(True)

sum_rewards = 0.0
nbr_episode = 10
for _ in range(nbr_episode):
    prod_line = Production_line(nbr_job_max, nbr_operation_max, nbr_machines, nbr_operator)
    job1 = Job("TEST1", 1,20000, nbr_operation_max)
    prod_line.add_job(job1)
    
    state = prod_line.get_state()
    done = False
    while not done:
        mask = prod_line.get_mask()
        action = agent.act(state,mask)
        next_state, reward, done = prod_line.step(action)
        
        agent.remember(state, action, reward, next_state, done)
        
        state = next_state
            
        sum_rewards += reward
        
    print(sum_rewards)
print('Mean evaluation return:', sum_rewards / nbr_episode)



planning = prod_line.get_gant_formated()

plan_df = pd.DataFrame()
for plan in planning:
    print(plan,"\n")
    df = pd.DataFrame(plan, columns =['Job','Machine', 'Operation', 'Start','Duration','Finish'])
    plan_df = pd.concat([plan_df, df], axis=0)

plan_df.reset_index(drop = True,inplace=True)

plan_df['Machine']= plan_df['Machine'].astype(str)
plan_df['Duration']= plan_df['Duration'].astype(int)




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
    
visualize(plan_df)