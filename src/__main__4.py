# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 16:40:36 2022
@author: LDE
"""
from Prod_line_4 import Production_line
import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset



from src.TF_env3 import TF_environment
from tensorforce import Environment, Agent

import src.utils as utils



import place_operator as utils_operators
import place_operations as utils_operations

import operator_stats as op_stats
from Operation3 import Operation


import os

import get_batch_to_produce as btp
import src.utils as utils
import operator_stats as op_stats

#load the current_date and create the prod_line object
current_date = pd.to_datetime("2022-10-13", format = "%Y-%m-%d")
prod_line = Production_line(current_date)

for op in prod_line.operations:
    if op.executable:
        print(op.operation_name, op.job_name)
        
prod_line.time += DateOffset(days = 19)
prod_line.update_executable()

op_dispo = prod_line.get_available_operators()
machine_dispo = prod_line.get_available_machines()
        
for op in prod_line.operations:
    if op.executable:
        print(op.operation_name, op.job_name)
        
        
        
        



