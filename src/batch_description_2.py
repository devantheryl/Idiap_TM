# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 15:19:01 2022

@author: LDE
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 14:47:47 2022

@author: LDE
"""

def get_batch_description():
    
    batch_description = {
    
    "1_20000" : {
        
        "BR" : {
            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
            
        },
        
        "TP" : {
            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        
        "MEL" : {

            "processable_on" : ["m3"],
            "processing_time" : 1,
            "expiration_time" : 2,
            "operator" : 3,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        
        "EX" : {
            "processable_on" : ["m4"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        
        "BB" : {

            "processable_on" : ["m0","m1"],
            "processing_time" : 4,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        
        "TM" : {

            "processable_on" : ["m2"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 4
        },
        
        "MILIEU" : {

            "processable_on" : ["m6"],
            "processing_time" : 3,
            "expiration_time" : 14,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 1
        },
        
        "PERRY" : {

            "processable_on" : ["m7"],
            "processing_time" : 4,
            "expiration_time" : 14,
            "operator" : 8,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "CAPS": {
            "processable_on" : ["m8"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        }
        
        
    },
    "1_6600" : {
        
        "BR" : {

            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
            
        },
        
        "TP" : {

            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        
        "MEL" : {
            
            "processable_on" : ["m3"],
            "processing_time" : 1,
            "expiration_time" : 2,
            "operator" : 3,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        
        "EX" : {
            "processable_on" : ["m4"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        
        "BB" : {

            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        
        "TM" : {
            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 4
        },
        
        "MILIEU" : {

            "processable_on" : ["m6"],
            "processing_time" : 1,
            "expiration_time" : 14,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 1
        },
        
        "PERRY" : {
            "processable_on" : ["m7"],
            "processing_time" : 2,
            "expiration_time" : 14,
            "operator" : 8,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "CAPS": {
            "processable_on" : ["m8"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        }
        
        
    },
    "3_20000" : {
        
        "BR" : {
            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
            
        },
        
        "TP" : {
            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        
        "MEL" : {
            "processable_on" : ["m3"],
            "processing_time" : 1,
            "expiration_time" : 2,
            "operator" : 3,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        
        "EX" : {
            "processable_on" : ["m4"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        
        "BB" : {
            "processable_on" : ["m0","m1"],
            "processing_time" : 4,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        
        "TM" : {

            "processable_on" : ["m2"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 4
        },
        
        "MILIEU" : {
            "processable_on" : ["m6"],
            "processing_time" : 3,
            "expiration_time" : 14,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 1
        },
        
        "PERRY" : {
            "processable_on" : ["m7"],
            "processing_time" : 4,
            "expiration_time" : 14,
            "operator" : 8,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "CAPS": {
            "processable_on" : ["m8"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        }
        
        
    },
    "3_6600" : {
        
        "BR" : {
            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
            
        },
        
        "TP" : {
            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        
        "MEL" : {
            "processable_on" : ["m3"],
            "processing_time" : 1,
            "expiration_time" : 2,
            "operator" : 3,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        
        "EX" : {
            "processable_on" : ["m4"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        
        "BB" : {
            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        
        "TM" : {
            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 4
        },
        
        "MILIEU" : {
            "processable_on" : ["m6"],
            "processing_time" : 1,
            "expiration_time" : 14,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 1
        },
        
        "PERRY" : {
            "processable_on" : ["m7"],
            "processing_time" : 2,
            "expiration_time" : 14,
            "operator" : 8,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "CAPS": {
            "processable_on" : ["m8"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        }
        
        
    },
    "6_20000" : {
        
        "BR_1" : {

            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
            
        },
        "BR_2" : {

            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
            
        },
        "TP_1" : {

            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "TP_2" : {

            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "MEL_1" : {
            "processable_on" : ["m3"],
            "processing_time" : 1,
            "expiration_time" : 2,
            "operator" : 3,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "MEL_2" : {

            "processable_on" : ["m3"],
            "processing_time" : 1,
            "expiration_time" : 2,
            "operator" : 3,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "EX_1" : {
            "processable_on" : ["m4"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "EX_2" : {

            "processable_on" : ["m4"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "BB_1" : {

            "processable_on" : ["m0","m1"],
            "processing_time" : 4,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "BB_2" : {

            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "TM_1" : {

            "processable_on" : ["m2"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 4
        },
        "TM_2" : {
            "processable_on" : ["m2"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 4
        },
        "MILIEU" : {
            "processable_on" : ["m6"],
            "processing_time" : 3,
            "expiration_time" : 14,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 1
        },
        "CF" : {
            "processable_on" : ["m5"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "PERRY" : {
            "processable_on" : ["m7"],
            "processing_time" : 4,
            "expiration_time" : 14,
            "operator" : 8,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "CAPS": {
            "processable_on" : ["m8"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        }
        
        
    },
    "6_6600" : {
        
        "BR_1" : {

            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
            
        },
        "BR_2" : {
            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
            
        },
        "TP_1" : {

            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "TP_2" : {
            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "MEL_1" : {
            "processable_on" : ["m3"],
            "processing_time" : 1,
            "expiration_time" : 2,
            "operator" : 3,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "MEL_2" : {
            "processable_on" : ["m3"],
            "processing_time" : 1,
            "expiration_time" : 2,
            "operator" : 3,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "EX_1" : {
            "processable_on" : ["m4"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "EX_2" : {
            "processable_on" : ["m4"],
            "processing_time" : 2,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "BB_1" : {
            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "BB_2" : {
            "processable_on" : ["m0","m1"],
            "processing_time" : 2,
            "expiration_time" : 12,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "TM_1" : {
            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 4
        },
        "TM_2" : {
            "processable_on" : ["m2"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 4
        },
        "MILIEU" : {
            "processable_on" : ["m6"],
            "processing_time" : 1,
            "expiration_time" : 14,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 1
        },
        "CF" : {
            "processable_on" : ["m5"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : False, 
            "QC_delay" : 0
        },
        "PERRY" : {
            "processable_on" : ["m7"],
            "processing_time" : 2,
            "expiration_time" : 14,
            "operator" : 8,
            "begin_day" : True, 
            "QC_delay" : 0
        },
        "CAPS": {
            "processable_on" : ["m8"],
            "processing_time" : 1,
            "expiration_time" : 60,
            "operator" : 2,
            "begin_day" : True, 
            "QC_delay" : 0
        }
        
        
    },
    
    "machines" : [
        "broyeur_b1", 
        "broyeur_b2", 
        "tamiseur_b2" , 
        "melangeur_b2", 
        "extrudeur_b2", 
        "combinaison_b",
        "millieu_b1" , 
        "perry_b2",
        "Capsulage"
        
    ]

    }
    
    return batch_description
