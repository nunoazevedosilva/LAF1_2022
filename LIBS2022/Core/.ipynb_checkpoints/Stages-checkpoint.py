
# coding: utf-8

# In[ ]:


import serial
import time
import numpy as np

#ser = serial.Serial("COM1", baudrate=9600,timeout=1,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

class Stage:

    def __init__(self,stage):
        self.stage=bytearray(str(stage),"utf-8")
        
    def on(self): #function just to turn the axis on
        return self.stage + b'MO'

    def off(self): #function just to turn the axis off
        return self.stage + b'MF'

    def home(self):
        return self.stage + b'OR2' # OR its the home set, and the extra 0 
                                   # is for the aditional movement
                                   
    def posA(self,x1): 
        return self.stage + b'PA' + bytearray(str(x1),"utf-8")

    def posR(self,x1): 
        return self.stage + b'PR' + bytearray(str(x1),"utf-8")

    def fposA(self): 
        return self.stage + b'PA?'





class Driver:

    def __init__(self,s1,s2,serial):
        self.s1=s1
        self.s2=s2
        self.serial=serial

    def on(self): #function just to turn the axis on
        self.serial.write(self.s1.on() + b";" + self.s2.on() + b"\r\n")
        self.home()

    def off(self): #function just to turn the axis off
        self.home()
        self.serial.write(self.s1.off() + b";" + self.s2.off() + b"\r\n")

    def home(self): #function just to send both axis to home
        self.serial.write(self.s1.home() + b";" + self.s2.home() + b"\r\n")
        
        c=self.state() # to know whats the state and current position of the both axis
        while (c[0]=='0' or c[1]=='0') or (float(c[2])!=float(0) or float(c[3])!=float(0)):
            #print(c,'Doing step')  #this while makes that the process of moving to a position only stops
            c=self.state()      # when done status of both axis are '1' and the position_read=postion_wanted
        c=self.state()

    def state(self): # function to read what's the state of both axis and position
        self.serial.write(b'1MD?;2MD?;1TP?;2TP?\r\n') # state is 1 if its done with movement and 0 if not
        b=self.serial.read(25).decode("utf-8").split("\r\n") # because it has extra stuff we filter out whats not important
        
        c=(b[0],b[1],b[2],b[3])
        return c

    def posA(self,s,x):
        self.serial.write(s.posA(x) + b"\r\n") #fazer o resto

    def fposA(self):
        self.serial.write(s.fposA(x) + b"\r\n") #fazer o resto

        

    def posAxy(self,x,y):
        self.serial.write(self.s1.posA(x)+b";"+self.s2.posA(y)+ b"\r\n")
        c=self.state() # to know whats the state and current position of the both axis
        while (c[0]=='0' or c[1]=='0') or (float(c[2])!=float(x) or float(c[3])!=float(y)):
            #print(c,'Doing step')  #this while makes that the process of moving to a position only stops
            c=self.state()      # when done status of both axis are '1' and the position_read=postion_wanted
        c=self.state()                         
        #print(c,'Step ended')   # this print is just to make sure it is where we want it

    def fposAxy(self):
        self.serial.write(self.s1.fposA()+b";"+self.s2.fposA()+ b"\r\n")
        time.sleep(0.5)
        m=self.serial.read_all()
        time.sleep(0.5)
        return m.decode("utf-8").split("\r\n")


