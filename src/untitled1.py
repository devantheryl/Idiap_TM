# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 09:38:26 2022

@author: LDE
"""

from datetime import datetime, timedelta, date
import numpy as np
import src.utils as utils
import pandas as pd
import os


file = "C:/Users/LDE/Prog/projet_master/digital_twins/data/Avancements des lots.xlsx"

def read_target_date(file):
    
    df = pd.read_excel(file,2)
    
    print(df)
    return df
    
    
#df =read_target_date(file)


test = np.array([1,0,0,0])

print((test <0).any() == True)