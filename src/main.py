from src.Job import Job
from src.Production_line import Production_line
from src.Machine import Machine
from src.Operation import Operation
from src.Agent import Agent
import numpy as np
import random
from datetime import datetime


prod_line = Production_line()
agent = Agent(prod_line)
job1 = Job("TEST1", 1,20000)
job2 = Job("TEST2", 1,20000)

prod_line.add_job(job1)
prod_line.add_job(job2)



for i in range(20):
    print("operations dispo :",agent.get_available_operation())
    print("decisions dispo : ",agent.get_available_actions())
    print("decision prise : ",agent.take_decision())
    
    
    state = prod_line.get_rl_formated_state()
    for s in state:
        print(s)
    print("=========================================")
    
    
