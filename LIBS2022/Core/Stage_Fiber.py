# -*- coding: utf-8 -*-
"""
Class and controllers for stage Fiber Laser
"""


class Stage_Fiber:
    
    def __init__(self):

        self.s=''
            
        
    def check_state(self):
        
        return True, [0,0]
        
    def turn_on(self):
        pass
    
    def turn_off(self): 
        pass

    def go_home(self):
        pass
    
    def move_to(self,x,y):
        pass


########################
    def move_single_axis(self,stage_axis,pos):
        pass

    def fposA(self):
        pass

    def fposAxy(self):
        pass