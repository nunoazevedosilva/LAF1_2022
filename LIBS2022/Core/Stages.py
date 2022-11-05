
# coding: utf-8

# In[ ]:


import serial
import numpy as np

from Core.Stage_NdYAG import *
from Core.Stage_demo import *
from Core.Stage_Fiber import *


class Stage_System:

    def __init__(self,system='NdYAG'):
        if system=='NdYAG':
            self.stage=Stage_NdYAG()
            
        elif system == 'Demo':
            self.stage = Stage_demo()
            
        elif system == 'Fiber':
            self.stage = Stage_Fiber()
    
    def check_state(self):
        """
        Checks the state of the stage system
        Returns
        -------
        bool True/False - if is ready
        [x,y] - current position
        """
        return self.stage.check_state()
    
    def turn_on(self):
        """
        Start the stage system
        """
        self.stage.turn_on()

    def turn_off(self):
        """
        Turns off the stage system
        """
        self.stage.turn_off()
    
    def go_home(self):
        """
        Send stages to the starting position
        """
        return self.stage.go_home()
        
    def current_position(self):
        """
        Gets the current position
        """
        
        return self.stage.check_state()[1]
    
    def move_to(self, x, y, z=0):
        """
        Moves to x,y position
        
        """
        self.stage.move_to(x=x,y=y,z=z)
    
    def rotate(self, theta):
        self.stage.rotate(theta)
    
