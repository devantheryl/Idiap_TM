# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 14:47:47 2022

@author: LDE
"""

def get_batch_description():
    
    batch_description = {
    
    "Batch_3.75_20000_REVERSE" : {
        
        "operation1" : {
            "type" : "operation",
            "number" : 1,
            "OF" : "POLBR",
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [3],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 1, 
            "QC_delay" : 0
            
        },
        
        "operation2" : {
            "type" : "operation",
            "number" : 3,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [5],
            "operator" : 2,
            "used_by" : [1],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        
        "operation3" : {
            "type" : "operation",
            "number" : 5,
            "processable_on" : [4],
            "processing_time" : 1,
            "expiration_time" : 2,
            "dependencies" : [7],
            "operator" : 3,
            "used_by" : [3],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        
        "operation4" : {
            "type" : "operation",
            "number" : 7,
            "processable_on" : [5],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [9],
            "operator" : 2,
            "used_by" : [5],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        
        "operation5" : {
            "type" : "operation",
            "number" : 9,
            "processable_on" : [1,2],
            "processing_time" : 4,
            "expiration_time" : 12,
            "dependencies" : [11],
            "operator" : 2,
            "used_by" : [7],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        
        "operation6" : {
            "type" : "operation",
            "number" : 11,
            "processable_on" : [3],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [9],
            "begin_day" : 1, 
            "QC_delay" : 4
        },
        
        "operation7" : {
            "type" : "operation",
            "number" : 13,
            "processable_on" : [7],
            "processing_time" : 3,
            "expiration_time" : 14,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 0, 
            "QC_delay" : 1
        },
        
        "operation9" : {
            "type" : "operation",
            "number" : 15,
            "processable_on" : [8],
            "processing_time" : 4,
            "expiration_time" : 14,
            "dependencies" : [],
            "operator" : 8,
            "used_by" : [13,11],
            "begin_day" : 1, 
            "QC_delay" : 0
        }
        
        
    },
    "Batch_3.75_6600_REVERSE" : {
        
        "operation1" : {
            "type" : "operation",
            "number" : 1,
            "OF" : "POLBR",
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [3],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 1, 
            "QC_delay" : 0
            
        },
        
        "operation2" : {
            "type" : "operation",
            "number" : 3,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [5],
            "operator" : 2,
            "used_by" : [1],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        
        "operation3" : {
            "type" : "operation",
            "number" : 5,
            "processable_on" : [4],
            "processing_time" : 1,
            "expiration_time" : 2,
            "dependencies" : [7],
            "operator" : 3,
            "used_by" : [3],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        
        "operation4" : {
            "type" : "operation",
            "number" : 7,
            "processable_on" : [5],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [9],
            "operator" : 2,
            "used_by" : [5],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        
        "operation5" : {
            "type" : "operation",
            "number" : 9,
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [11],
            "operator" : 2,
            "used_by" : [7],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        
        "operation6" : {
            "type" : "operation",
            "number" : 11,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [9],
            "begin_day" : 1, 
            "QC_delay" : 4
        },
        
        "operation7" : {
            "type" : "operation",
            "number" : 13,
            "processable_on" : [7],
            "processing_time" : 1,
            "expiration_time" : 14,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 0, 
            "QC_delay" : 1
        },
        
        "operation9" : {
            "type" : "operation",
            "number" : 15,
            "processable_on" : [8],
            "processing_time" : 2,
            "expiration_time" : 14,
            "dependencies" : [],
            "operator" : 8,
            "used_by" : [13,11],
            "begin_day" : 1, 
            "QC_delay" : 0
        }
        
        
    },
    "Batch_11.25_20000_REVERSE" : {
        
        "operation1" : {
            "type" : "operation",
            "number" : 1,
            "OF" : "POLBR",
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [3],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 1, 
            "QC_delay" : 0
            
        },
        
        "operation2" : {
            "type" : "operation",
            "number" : 3,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [5],
            "operator" : 2,
            "used_by" : [1],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        
        "operation3" : {
            "type" : "operation",
            "number" : 5,
            "processable_on" : [4],
            "processing_time" : 1,
            "expiration_time" : 2,
            "dependencies" : [7],
            "operator" : 3,
            "used_by" : [3],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        
        "operation4" : {
            "type" : "operation",
            "number" : 7,
            "processable_on" : [5],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [9],
            "operator" : 2,
            "used_by" : [5],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        
        "operation5" : {
            "type" : "operation",
            "number" : 9,
            "processable_on" : [1,2],
            "processing_time" : 4,
            "expiration_time" : 12,
            "dependencies" : [11],
            "operator" : 2,
            "used_by" : [7],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        
        "operation6" : {
            "type" : "operation",
            "number" : 11,
            "processable_on" : [3],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [9],
            "begin_day" : 1, 
            "QC_delay" : 4
        },
        
        "operation7" : {
            "type" : "operation",
            "number" : 13,
            "processable_on" : [7],
            "processing_time" : 3,
            "expiration_time" : 14,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 0, 
            "QC_delay" : 1
        },
        
        "operation9" : {
            "type" : "operation",
            "number" : 15,
            "processable_on" : [8],
            "processing_time" : 4,
            "expiration_time" : 14,
            "dependencies" : [],
            "operator" : 8,
            "used_by" : [13,11],
            "begin_day" : 1, 
            "QC_delay" : 0
        }
        
        
    },
    "Batch_11.25_6600_REVERSE" : {
        
        "operation1" : {
            "type" : "operation",
            "number" : 1,
            "OF" : "POLBR",
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [3],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 1, 
            "QC_delay" : 0
            
        },
        
        "operation2" : {
            "type" : "operation",
            "number" : 3,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [5],
            "operator" : 2,
            "used_by" : [1],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        
        "operation3" : {
            "type" : "operation",
            "number" : 5,
            "processable_on" : [4],
            "processing_time" : 1,
            "expiration_time" : 2,
            "dependencies" : [7],
            "operator" : 3,
            "used_by" : [3],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        
        "operation4" : {
            "type" : "operation",
            "number" : 7,
            "processable_on" : [6],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [9],
            "operator" : 2,
            "used_by" : [5],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        
        "operation5" : {
            "type" : "operation",
            "number" : 9,
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [11],
            "operator" : 2,
            "used_by" : [7],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        
        "operation6" : {
            "type" : "operation",
            "number" : 11,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [9],
            "begin_day" : 1, 
            "QC_delay" : 4
        },
        
        "operation7" : {
            "type" : "operation",
            "number" : 13,
            "processable_on" : [7],
            "processing_time" : 1,
            "expiration_time" : 14,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 0, 
            "QC_delay" : 1
        },
        
        "operation9" : {
            "type" : "operation",
            "number" : 15,
            "processable_on" : [8],
            "processing_time" : 2,
            "expiration_time" : 14,
            "dependencies" : [],
            "operator" : 8,
            "used_by" : [13,11],
            "begin_day" : 1, 
            "QC_delay" : 0
        }
        
        
    },
    "Batch_22.50_20000_REVERSE" : {
        
        "operation1" : {
            "type" : "operation",
            "name" : "broyage_poly",
            "number" : 1,
            "OF" : "POLBR",
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [3],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 1, 
            "QC_delay" : 0
            
        },
        "operation1.2" : {
            "type" : "operation",
            "number" : 2,
            "OF" : "POLBR",
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [4],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 1, 
            "QC_delay" : 0
            
        },
        "operation2" : {
            "type" : "operation",
            "number" : 3,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [5],
            "operator" : 2,
            "used_by" : [1],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation2.2" : {
            "type" : "operation",
            "number" : 4,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [6],
            "operator" : 2,
            "used_by" : [2],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation3" : {
            "type" : "operation",
            "number" : 5,
            "processable_on" : [4],
            "processing_time" : 1,
            "expiration_time" : 2,
            "dependencies" : [7],
            "operator" : 3,
            "used_by" : [3],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation3.2" : {
            "type" : "operation",
            "number" : 6,
            "processable_on" : [4],
            "processing_time" : 1,
            "expiration_time" : 2,
            "dependencies" : [8],
            "operator" : 3,
            "used_by" : [4],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation4" : {
            "type" : "operation",
            "number" : 7,
            "processable_on" : [5],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [9],
            "operator" : 2,
            "used_by" : [5],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        "operation4.2" : {
            "type" : "operation",
            "number" : 8,
            "processable_on" : [5],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [10],
            "operator" : 2,
            "used_by" : [6],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        "operation5" : {
            "type" : "operation",
            "number" : 9,
            "processable_on" : [1,2],
            "processing_time" : 4,
            "expiration_time" : 12,
            "dependencies" : [11],
            "operator" : 2,
            "used_by" : [7],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        "operation5.2" : {
            "type" : "operation",
            "number" : 10,
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [12],
            "operator" : 2,
            "used_by" : [8],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        "operation6" : {
            "type" : "operation",
            "number" : 11,
            "processable_on" : [3],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [14],
            "operator" : 2,
            "used_by" : [9],
            "begin_day" : 1, 
            "QC_delay" : 4
        },
        "operation6.2" : {
            "type" : "operation",
            "number" : 12,
            "processable_on" : [3],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [14],
            "operator" : 2,
            "used_by" : [10],
            "begin_day" : 1, 
            "QC_delay" : 4
        },
        "operation7" : {
            "type" : "operation",
            "number" : 13,
            "processable_on" : [7],
            "processing_time" : 3,
            "expiration_time" : 14,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 0, 
            "QC_delay" : 1
        },
        "operation8" : {
            "type" : "operation",
            "number" : 14,
            "processable_on" : [6],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [11,12],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation9" : {
            "type" : "operation",
            "number" : 15,
            "processable_on" : [8],
            "processing_time" : 4,
            "expiration_time" : 14,
            "dependencies" : [],
            "operator" : 8,
            "used_by" : [13,14],
            "begin_day" : 1, 
            "QC_delay" : 0
        }
        
        
    },
    "Batch_22.50_6600_REVERSE" : {
        
        "operation1" : {
            "type" : "operation",
            "name" : "broyage_poly",
            "number" : 1,
            "OF" : "POLBR",
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [3],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 1, 
            "QC_delay" : 0
            
        },
        "operation1.2" : {
            "type" : "operation",
            "number" : 2,
            "OF" : "POLBR",
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [4],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 1, 
            "QC_delay" : 0
            
        },
        "operation2" : {
            "type" : "operation",
            "number" : 3,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [5],
            "operator" : 2,
            "used_by" : [1],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation2.2" : {
            "type" : "operation",
            "number" : 4,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [6],
            "operator" : 2,
            "used_by" : [2],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation3" : {
            "type" : "operation",
            "number" : 5,
            "processable_on" : [4],
            "processing_time" : 1,
            "expiration_time" : 2,
            "dependencies" : [7],
            "operator" : 3,
            "used_by" : [3],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation3.2" : {
            "type" : "operation",
            "number" : 6,
            "processable_on" : [4],
            "processing_time" : 1,
            "expiration_time" : 2,
            "dependencies" : [8],
            "operator" : 3,
            "used_by" : [4],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation4" : {
            "type" : "operation",
            "number" : 7,
            "processable_on" : [5],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [9],
            "operator" : 2,
            "used_by" : [5],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        "operation4.2" : {
            "type" : "operation",
            "number" : 8,
            "processable_on" : [5],
            "processing_time" : 2,
            "expiration_time" : 60,
            "dependencies" : [10],
            "operator" : 2,
            "used_by" : [6],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        "operation5" : {
            "type" : "operation",
            "number" : 9,
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [11],
            "operator" : 2,
            "used_by" : [7],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        "operation5.2" : {
            "type" : "operation",
            "number" : 10,
            "processable_on" : [1,2],
            "processing_time" : 2,
            "expiration_time" : 12,
            "dependencies" : [12],
            "operator" : 2,
            "used_by" : [8],
            "begin_day" : 1, 
            "QC_delay" : 0
        },
        "operation6" : {
            "type" : "operation",
            "number" : 11,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [14],
            "operator" : 2,
            "used_by" : [9],
            "begin_day" : 1, 
            "QC_delay" : 4
        },
        "operation6.2" : {
            "type" : "operation",
            "number" : 12,
            "processable_on" : [3],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [14],
            "operator" : 2,
            "used_by" : [10],
            "begin_day" : 1, 
            "QC_delay" : 4
        },
        "operation7" : {
            "type" : "operation",
            "number" : 13,
            "processable_on" : [7],
            "processing_time" : 1,
            "expiration_time" : 14,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [],
            "begin_day" : 0, 
            "QC_delay" : 1
        },
        "operation8" : {
            "type" : "operation",
            "number" : 14,
            "processable_on" : [6],
            "processing_time" : 1,
            "expiration_time" : 60,
            "dependencies" : [15],
            "operator" : 2,
            "used_by" : [11,12],
            "begin_day" : 0, 
            "QC_delay" : 0
        },
        "operation9" : {
            "type" : "operation",
            "number" : 15,
            "processable_on" : [8],
            "processing_time" : 2,
            "expiration_time" : 14,
            "dependencies" : [],
            "operator" : 8,
            "used_by" : [13,14],
            "begin_day" : 1, 
            "QC_delay" : 0
        }
        
        
    },
    
    
    "action_space" : {
        "1" : [1,2],
        "2" : [3],
        "3" : [4,5],
        "4" : [6],
        "5" : [1,2],
        "6" : [3],
        "7" : [8],
        "8" : [7],
        "9" : [9],
        "10" : [10],
        "11" : [11],
        "12" : [12],
        "13" : [13],
        "14" : [14]        
    }, 
    "action_space_reverse" : {
        "1" : [1,2],
        "2" : [1,2],
        "3" : [3],
        "4" : [3],
        "5" : [4],
        "6" : [4],
        "7" : [5],
        "8" : [5],
        "9" : [1,2],
        "10" : [1,2],
        "11" : [3],
        "12" : [3],
        "13" : [7],
        "14" : [6],
        "15" : [8]       
    }, 
    "machines" : [
        "broyeur_b1", 
        "broyeur_b2", 
        "tamiseur_b2" , 
        "melangeur_b2", 
        "extrudeur_b2", 
        "combinaison_b",
        "millieu_b1" , 
        "perry_b2"
        
    ]

    }
    
    return batch_description
