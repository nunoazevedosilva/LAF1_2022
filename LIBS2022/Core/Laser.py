
import serial
from Core.Laser_NdYAG import *
from Core.Laser_Demo import *
from Core.Laser_Fiber import *
 

class Laser_System:

    def __init__(self,system='NdYAG', parameters={}):
        if system=='NdYAG':
            self.laser = Laser_NdYAG(parameters=parameters)
        elif system=='Demo':
            self.laser = Laser_Demo()
        elif system=='Fiber':
            self.laser =  Laser_Fiber(parameters=parameters)
            
            
    def start_laser(self):
        self.laser.start_laser()
    
    def getting_ready(self):
        return self.laser.getting_ready()
    
    def pause(self):
        self.laser.pause()
    
    def single_shot(self):
        self.laser.single_shot()
    
    def multi_shot(self):
        pass
        #self.laser.multi_shot()
        
    def set_parameters(self, parameters):
        self.laser.set_parameters(parameters)
        #pass
        
    