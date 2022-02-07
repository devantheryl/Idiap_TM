# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 14:56:59 2022

@author: LDE
"""

from collections import deque
import numpy as np

from datetime import datetime, timedelta
time1 = datetime.fromisoformat('2022-01-12 00:00:00')
time2 = datetime.fromisoformat("2022-01-11 00:08:00")

print(time1 == time2)

total = time2-time1
print(total.days)


test = deque(maxlen=10)

test.append((5,7,8,89,9,0,))
test.append((5,7,8,89,9,0,))
test.append((5,7,8,89,9,0,))
test.append((5,7,8,89,9,0,))
test.append((5,7,8,89,9,0,))

state = np.ndarray((11))
sum_state = ()



            
for machine in range(10):
    sum_state += ("12",)
    
sum_state += (12,)
state[:] = sum_state
state = np.array(state, dtype =object).flatten()
print(state.shape)



