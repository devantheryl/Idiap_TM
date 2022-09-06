# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 14:09:52 2022

@author: LDE
"""

import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset

def place_operations(agent, environment, df_futur_machine, targets, formulations, scales, batch_names):
    
    planning_tot_max = None
    lead_time_tot = []
    for j in range(len(targets)):
        planning_max = None
        lead_time_min = 1000
        print("job : ", j)

        for tentative in range(100):
            reward_tot = 0
            
            futur_state = df_futur_machine.copy()
    
            # Initialize episode
            target = pd.to_datetime(targets[j])
            formulation = formulations[j]
            scale = scales[j]
            batch_name = batch_names[j]
    
            environment.job_name = batch_name
            environment.target = target
            environment.formulation = formulation 
            environment.echelle = scale
            environment.futur_state = futur_state
            states = environment.reset()
            reward_batch = 0
            terminal = False
            internals = agent.initial_internals()
    
            while not terminal:
                 # Episode timestep
                actions, internals = agent.act(states=states, internals = internals, independent=True, deterministic = False)
                states, terminal, reward = environment.execute(actions=actions)
    
                reward_batch += reward
    
            futur_state = environment.get_env().state_full
            reward_tot += reward_batch
            planning = environment.get_env().get_gant_formated()
            
            count = (planning['Start'] == 0).sum()
            if count == 0:
                lead_time = environment.get_env().job.lead_time
                print("tentative : ", tentative, "  : no break", " lead_time : ", lead_time)
                if lead_time < lead_time_min:
                    print("new plann : ", np.mean(lead_time))
    
                    planning_max = planning.copy()
                    futur_state_max = futur_state.copy()
                    lead_time_min = lead_time
        planning_tot_max  = pd.concat([planning_tot_max,planning_max])
        
        
        df_futur_machine = futur_state_max
        #merge occupation of mélange et extrudeur (m4 et m5)
        merge_melex = np.where(df_futur_machine.m4 + df_futur_machine.m5 >=1,1,0)
        df_futur_machine.loc[:,"m4"] = merge_melex
        df_futur_machine.loc[:,"m5"] = merge_melex
        
        lead_time_tot.append(lead_time_min)
        
    print("lead time mean : ",np.mean(lead_time_tot))
    
    return planning_tot_max, lead_time_tot