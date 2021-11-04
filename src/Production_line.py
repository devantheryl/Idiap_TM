
from src.Machine import Machine
from src.Operation import Operation
from src.Job import Job
import networkx as nx 
import numpy as np
import json

all_machine = ["broyeur_b1" , "broyeur_b2", "tamiseur_b2" , "melangeur_b1" , 
               "melangeur_b2", "extrudeur_b2" , "combinaison_b",
               "millieu_b1" , "perry_b2", "sortie_lyo_b2" , "capsulage_b1",
               "IV_b" , "envoi_irr_g" , "retour_irr_g"]
max_jobs = 2
nbr_operations = 14
nbr_machine = 14


class Production_line:
        
        def __init__(self,time = 0):
    
            self.time = time
            self.jobs = []
            self.planning = []
            self.plateau_operation = np.ndarray((max_jobs,nbr_operations),dtype = object)#to store the state
            self.plateau_machine = np.ndarray((nbr_machine),dtype = object)#to store the state
            
            self.action_space = self.create_action_space()
            self.create_machine()
            
        def create_machine(self):
            
            for i, name in enumerate(all_machine):
                the_machine = Machine(i+1,name)
                self.plateau_machine[i] = the_machine
                
        
        def add_job(self,job):
            
            free_rows = self.check_free_rows()
            if len(free_rows) != 0:
                free_row = free_rows[0]
                self.add_job_to_plateau(job,free_row)
                self.jobs.append(job)
                return True
            else:
                return False
            
        def add_job_to_plateau(self,job,row):
            operations = job.get_all_operations()
            for operation in operations:
                self.plateau_operation[row, operation.get_operation_number()-1] = operation
        
        def execute_action(self,action):
            
            job_to_schedule = action[0]
            operation_to_schedule = action[1]
            machine_to_schedule = action[2]
            
            if action != "forward":
                self.plateau_operation[job_to_schedule-1,operation_to_schedule-1].set_status(1) #status = en cours
                #set the start time of the operation and the machine on wich it's scheduled
                self.plateau_operation[job_to_schedule-1,operation_to_schedule-1].set_start_time(self.time)
                self.plateau_operation[job_to_schedule-1,operation_to_schedule-1].set_processed_on(machine_to_schedule)
                
                #assign the operation on the machine
                self.plateau_machine[machine_to_schedule-1].assign_operation((job_to_schedule,operation_to_schedule))
            else:
                #stock the planning à time t
                self.build_planning()
                self.time +=1
                
                #update operation and machine
                planned_operation = self.get_planned_operation()
                for state in planned_operation:
                    
                    coord_op = state[1]
                    self.plateau_operation[coord_op[0]-1,coord_op[1]-1].forward()
                    if self.plateau_operation[coord_op[0]-1,coord_op[1]-1].get_status() == 2:
                        self.plateau_operation[coord_op[0]-1,coord_op[1]-1].set_end_time(self.time)
                        self.plateau_machine[state[0]-1].remove_operation()
                        
                #increment lead_time for all job
                for job in self.jobs:
                    job.increment_lead_time(1)
                    
                #update the operation that are newly executable
                self.check_update_expiration_time()
                self.check_update_executable()
                
                    
                
            

        def check_free_rows(self):
            free_rows = []
            for i in range(max_jobs):
                free = True
                for j in range(nbr_operations):
                    if self.plateau_operation[i,j] != None:
                        free = False
                if free:
                    free_rows.append(i)
                    
            return free_rows
                    
        def create_action_space(nbr_job_max):
            with open("src/batch_description.json") as json_file:
                batch_description = json.load(json_file)
            actions = []
            for x,y in batch_description["action_space"].items():
                for i in range(max_jobs):
                    for machine in y:
                        actions.append((i+1,int(x),machine))   
            return actions
            
        def get_action_space(self):
            return self.action_space
        
        def get_plateau_operation(self):
            return self.plateau_operation
        
        def get_plateau_machine(self):
            return self.plateau_machine
            
        def get_rl_formated_state(self):
            
            state = []
            for job in range(max_jobs):
                for operation in range(nbr_operations):
                    the_operation = self.plateau_operation[job,operation]
                    if the_operation != None:
                        state.append(the_operation.get_state())
                    else:
                        state.append(Operation.get_default_state())
            for machine in self.plateau_machine:
                state.append(machine.get_state())
            return state
    
        def build_planning(self):
            machine_planning = []
            for machine in self.plateau_machine:
                machine_planning.append(machine.get_operation())
            self.planning.append(machine_planning)
            
        def get_gant_formated(self):
            
            planning = []
            for job in self.jobs:
                planning.append(job.build_gant_formated())
                
            return planning
            
        def get_planning(self):
            return self.planning
    
        def get_planned_operation(self):
            
            planned_operation = []
            for machine in self.plateau_machine:
                state = machine.get_state()
                if state["status"] == 1:
                    planned_operation.append((machine.get_number(),state["operation"]))
            
            return planned_operation
        
        def check_update_executable(self):
            for job in range(max_jobs):
                for operation in range(nbr_operations):
                    if self.plateau_operation[job,operation] != None:
                        if self.plateau_operation[job,operation].get_status() == 0 and self.plateau_operation[job,operation].get_executable()==False:
                            dependencies = self.plateau_operation[job,operation].get_dependencies()
                            ok = True
                            for dependencie in dependencies:
                                if self.plateau_operation[job,dependencie-1].get_status() != 2:
                                    ok = False
                            if ok:
                                self.plateau_operation[job,operation].set_executable(True)
        
        def check_update_expiration_time(self):
            for job_coor in range(max_jobs):
                for operation_coor in range(nbr_operations):
                    if self.plateau_operation[job_coor, operation_coor] != None:
                        #si l'opération est terminée (satus = 2)
                        if self.plateau_operation[job_coor,operation_coor].get_status() == 2:
                            used_by = self.plateau_operation[job_coor,operation_coor].get_used_by()
                            #si l'operation suivante n'a pas encore commencé (pas encore consommé l'opération précédente)
                            if self.plateau_operation[job_coor,used_by-1].get_status() == 0:
                                
                                if self.plateau_operation[job_coor,operation_coor].decrease_get_expiration_time() == 0:
                                    job_name = self.plateau_operation[job_coor,operation_coor].get_job_name()
                                    
                                    for job in self.jobs:
                                        if job.get_job_name() == job_name:
                                            #on a trouvé le job et sa ligne dans le plateau_operation
                                            #on recrée le job numero "used_by"
                                            new_operation = job.create_operation(operation_coor+1)
                                            #on remplace l'operation dans le plateau
                                            self.plateau_operation[job_coor,operation_coor] = new_operation
                                            #l'operation suivante n'est plus executable
                                            self.plateau_operation[job_coor,used_by-1].set_executable(False)
                                    
                            
            
                                
            
            
                    
        
        
            
                
            
            
            
                