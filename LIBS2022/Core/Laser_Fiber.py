# -*- coding: utf-8 -*-
"""
Class for controlling a demo laser
"""

import time
import serial
        
#########################################################################################
######################################NDYAG##############################################   

class Laser_Fiber:
    def __init__(self, parameters={}):
        self.s = ''
        self.syncray = SyncRay()
        
    def check_state(self):
        return True
    
    def start_laser(self):
        self.syncray.load_state()
        pass


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
    
    def getting_ready(self):
        pass 
    
    def turn_on_lamp(self):
        pass
    
    def turn_off_lamp(self):
        pass
    
    def set_parameters(self):
        pass
    
    def single_shot(self):
        self.syncray.arm()
        pass
    
    def shutter(self):
        pass


class SyncRay:
    
    def __init__(self):
        #serial
        pass
    
    def arm(self):
        pass
    
    def disarm(self):
        pass
    
    def save_state(self):
        pass
    
    def load_state(self):
        pass
    
    

