# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 09:38:26 2022

@author: LDE
"""

from datetime import datetime, timedelta, date
import numpy as np
time = []

time.append(datetime.fromisoformat('2022-01-01 00:00:00'))
time.append(datetime.fromisoformat('2022-01-10 00:00:00'))
time.append(datetime.fromisoformat('2022-03-01 00:00:00'))

print(time[0].weekday())


test = np.linspace(1,10,10)
test[0:1] -=10
print(test)

for i in range(4):
    print(i)
    
    
    
print(time[0] < time[1])