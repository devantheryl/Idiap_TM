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
print(test+10)
test = np.roll(test, 1)
print(test)