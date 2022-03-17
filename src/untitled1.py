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
from random import sample


list1 = [0,1,2,3]
nbr0 = 0
nbr1 = 0
nbr2 = 0
nbr3 = 0

it = 100000

for i in range(it):
    if sample(list1,1)[0] == 0:
         nbr0+=1   

    if sample(list1,1)[0] == 1:
         nbr1+=1 
         
    if sample(list1,1)[0] == 2:
         nbr2+=1
         
    if sample(list1,1)[0] == 3:
         nbr3+=1 


print(nbr0/it)
print(nbr1/it)
print(nbr2/it)
print(nbr3/it)