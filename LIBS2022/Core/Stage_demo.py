# -*- coding: utf-8 -*-
"""
Class and controllers for demo stages
"""

import serial
import time
import numpy as np

#########################################################################################
######################################Demo##############################################    

class Stage_demo:
    
    def __init__(self):

        self.s=''
            
        
    def check_state(self):
        
        return True, [0,0]
        
    def turn_on(self):
        pass
    
    def turn_off(self): 
        pass

    def go_home(self):
        return True, [0,0]
        
    
    def move_to(self,x,y,z):
        pass
    
    def rotate(self, theta):
        pass


########################
    def move_single_axis(self,stage_axis,pos):
        pass

    def fposA(self):
        pass

    def fposAxy(self):
        pass