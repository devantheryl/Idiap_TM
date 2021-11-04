import src.Machine as Machine

class Operation:
        
    def __init__(self, job_name, operation_number, processable_on, processing_time,
                 nbr_of_sucessor, expiration_time, dependencies, operator, used_by, 
                 executable = False, status = 0, remaining_time = -1 ):
         
        self.job_name = job_name
        self.operation_number = operation_number
        self.processable_on = processable_on
        self.status = 0 #0:non-attribué, 1:en cours, 2:terminé, 3:used, 4:doens't exist
        self.processing_time = processing_time
        self.nbr_of_sucessor = nbr_of_sucessor
        self.expiration_time = expiration_time
        self.dependencies = dependencies
        self.remaining_time = remaining_time
        self.executable = executable
        self.operator = operator
        self.used_by = used_by
        self.start_time = 0.0
        self.end_time = 0.0
        self.processed_on = 0
        
        

    def get_status(self):
        return self.status
    
    def set_status(self,status):
        self.status = status
        
    def set_start_time(self,time):
        self.start_time = float(time)
        
    def get_start_time(self):
        return self.start_time
    
    def get_end_time(self):
        return self.end_time
        
    def set_end_time(self,time):
        self.end_time = float(time)
        
    def set_processed_on(self,machine):
        self.processed_on = machine
    
    def get_processed_on(self):
        return self.processed_on
        
    def get_dependencies(self):
        return self.dependencies
        
    def get_operation_number (self):
        return self.operation_number
    
    def get_job_name(self):
        return self.job_name
    
    def get_processable_on(self):
        return self.processable_on
    
    def get_executable(self):
        return self.executable

    def set_executable(self,state):
        self.executable = state
    
    def get_used_by(self):
        return self.used_by
    def get_operator(self):
        return self.operator
        
    def get_features(self):
        return {"job_name" : self.job_name,
                "operation_number" : self.operation_number,
                "processable_on" : self.processable_on,
                "status" : self.status,
                "processing_time" : self.processing_time,
                "nbr_of_sucessor" : self.nbr_of_sucessor,
                "expiration_time" : self.expiration_time,
                "dependencies" : self.dependencies,
                "remaining_time" : self.remaining_time,
                "executable" : self.executable,
                "operator" : self.operator,
                "used_by" : self.used_by}
                
    def get_state(self):
        return {
                "status" : self.status,
                "processing_time" : self.processing_time,
                "nbr_of_sucessor" : self.nbr_of_sucessor,
                "expiration_time" : self.expiration_time,
                "remaining_time" : self.remaining_time,
                "executable" : self.executable
                }
    def get_default_state():
        return {
                "status" : 4,
                "processing_time" : 0,
                "nbr_of_sucessor" : 0,
                "expiration_time" : 0,
                "remaining_time" : 0,
                "executable" : False
                }
    def forward(self):
        self.processing_time = self.processing_time -1
        if self.processing_time == 0:
            self.status =2
        
    def decrease_get_expiration_time(self):
        self.expiration_time = self.expiration_time-1
        return self.expiration_time
        
    