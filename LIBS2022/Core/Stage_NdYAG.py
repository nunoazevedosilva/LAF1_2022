# -*- coding: utf-8 -*-
"""
Class controllers for stage NDYAG
"""


import serial
from PyQt5.QtCore import QThread
import numpy as np


            
class stage_axis:

    def __init__(self,stage):
        self.stage=bytearray(str(stage),"utf-8")
        
    def on(self): #function just to turn the axis on
        return self.stage + b'MO'

    def off(self): #function just to turn the axis off
        return self.stage + b'MF'
    
    def home(self): 
        return self.stage + b'PA?'
    
    
                                   
    def move_to(self,pos): 
        return self.stage + b'PA' + bytearray(str(pos),"utf-8")


##########################
    def posR(self,x1): 
        return self.stage + b'PR' + bytearray(str(x1),"utf-8")
    
    def home_2(self):
        return self.stage + b'OR2' # OR its the home set, and the extra 0 
                                   # is for the aditional movement
##########################
    
class Stage_NdYAG:
    
    def __init__(self):

        self.stage_x=stage_axis(1)
        self.stage_y=stage_axis(2)
        
        self.serial=serial.Serial("COM1", baudrate=9600,timeout=1,parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
            
        
    def check_state(self):
        self.serial.write(b'1MD?;2MD?;1TP?;2TP?\r\n') # state is 1 if its done with movement and 0 if not
        b=self.serial.read(25).decode("utf-8").split("\r\n") # because it has extra stuff we filter out whats not important
        
        ##Whats this? check
        c=(b[0],b[1],b[2],b[3])
        
        print(c)
        
        
        is_ready = not bool(c[0]=='0' or c[1]=='0')
        
        current_position = [float(c[2]),float(c[3])]
        
        return is_ready, current_position
    
        
    def turn_on(self): #function just to turn the axis on
        self.serial.write(self.stage_x.on() + b";" + self.stage_y.on() + b"\r\n")
       

    def turn_off(self): #function just to turn the axis off
        print("Turning off the stages")
        self.serial.write(self.stage_x.off() + b";" + self.stage_y.off() + b"\r\n")

    def go_home(self): #function just to send both axis to home
        self.serial.write(self.stage_x.home() + b";" + self.stage_y.home() + b"\r\n")
        self.serial.write(self.stage_x.home_2() + b";" + self.stage_y.home_2() + b"\r\n")
        #self.serial.write(self.stage_x.fposA()+b";"+self.stage_y.fposA()+ b"\r\n")
        
        #check if the movement ended
        is_ready,position=self.check_state()
        while not is_ready or position!=[float(0),float(0)]:
            is_ready, position= self.check_state()
            
        is_ready, position = self.check_state()
        return is_ready, position
    
    def move_to(self,x,y,z=0):
        self.serial.write(self.stage_x.move_to(x)+b";"+self.stage_y.move_to(y)+ b"\r\n")
        
        #check if the movement ended
        
        is_ready,position=self.check_state()
        
        #comentei isto
        #while not is_ready:
            #is_ready,position=self.check_state()
            
                    
    
    def rotate(self, theta):
        pass


########################
    def move_single_axis(self,stage_axis,pos):
        self.serial.write(stage_axis.posA(pos) + b"\r\n") #fazer o resto

    def fposAxy(self):
        self.serial.write(self.s1.fposA()+b";"+self.s2.fposA()+ b"\r\n")
        QThread.msleep(500)
        m=self.serial.read_all()
        QThread.msleep(500)
        return m.decode("utf-8").split("\r\n")