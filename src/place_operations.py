# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 14:09:52 2022

@author: LDE
"""

import pandas as pd
import numpy as np

def place_operations(agent, environment, df_futur_machine, targets, formulations, scales, batch_names):
    
    planning_tot_max = None
    lead_time_tot = []
    
    prod_line = environment.get_env()
    
    for j in range(len(targets)):
        planning_max = None
        lead_time_min = 1000
        print("job : ", j)

        for tentative in range(10):
            reward_tot = 0
            
            state = df_futur_machine.copy()
    
            # Initialize episode
            target = pd.to_datetime(targets[j])
            formulation = formulations[j]
            scale = scales[j]
            batch_name = batch_names[j]
    
            prod_line.add_job(target,formulation,scale,batch_name)
    
            prod_line.state = state
            states = environment.reset()
            reward_batch = 0
            terminal = False
            internals = agent.initial_internals()
    
            while not terminal:
                 # Episode timestep
                actions, internals = agent.act(states=states, internals = internals, independent=True, deterministic = False)
                states, terminal, reward = environment.execute(actions=actions)
    
                reward_batch += reward
    
            futur_state = prod_line.state
            reward_tot += reward_batch
            planning = prod_line.get_gant_formated()
            
            count = (planning['Start'] == 0).sum()
            if count == 0:
                lead_time = prod_line.job.lead_time
                print("tentative : ", tentative, "  : no break", " lead_time : ", lead_time)
                if lead_time < lead_time_min:
                    print("new plann : ", np.mean(lead_time))
    
                    planning_max = planning.copy()
                    futur_state_max = futur_state.copy()
                    lead_time_min = lead_time
        planning_tot_max  = pd.concat([planning_tot_max,planning_max])
        
        
        df_futur_machine = futur_state_max
        #merge occupation of mélange et extrudeur (m3 et m4)
        merge_melex = np.where(df_futur_machine.m3 + df_futur_machine.m4 >=1,1,0)
        df_futur_machine.loc[:,"m3"] = merge_melex
        df_futur_machine.loc[:,"m4"] = merge_melex
        
        lead_time_tot.append(lead_time_min)
        
    print("lead time mean : ",np.mean(lead_time_tot))
    
    return planning_tot_max, lead_time_tot