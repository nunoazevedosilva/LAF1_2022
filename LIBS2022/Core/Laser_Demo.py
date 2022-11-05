# -*- coding: utf-8 -*-
"""
Class for controlling a demo laser
"""

import time
import serial
        
#########################################################################################
######################################NDYAG##############################################   

class Laser_Demo:
    def __init__(self, parameters={}):
        self.s = ''
        self.delay = 0
        self.temp = 300
        self.cdelay=0
        
    def check_state(self):
        return True
    
    def start_laser(self):
        pass

    def getting_ready(self):
        time.sleep(0.05)
        current_temp = self.temp
        if current_temp<326: 
            self.temp += 1
            return True, current_temp
        else: 
            return False, current_temp
    
    def cooler_heating(self):
        pass
    
    def pause(self):
        pass
    
    def get_cooler_temperature(self):
        pass
                    
        
    def open_shutter(self):
        pass
    
    def close_shutter(self):
        pass
    
    def turn_on_lamp(self):
        pass
    
    def turn_off_lamp(self):
        pass
    
    def get_Qs(self):
        pass
    
    def set_Qs(self,delay):
        pass
    
    def single_shot(self):
        pass
    
    def shutter(self):
        pass
    
    def set_parameters(self,parameters):
        pass

