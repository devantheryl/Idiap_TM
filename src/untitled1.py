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


# Python code to demonstrate
# to convert dictionary into string
# using str()
  
# initialising dictionary
test1 = { "testname" : "akshat",
          "test2name" : "manjeet",
          "test3name" : "nikhil"}
  
# print original dictionary
print (type(test1))
print ("initial dictionary = ", test1)
  
# convert dictionary into string
# using str
result = str(test1)
  
# print resulting string
print ("\n", type(result))
print ("final string = ", result)