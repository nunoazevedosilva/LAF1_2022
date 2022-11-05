# -*- coding: utf-8 -*-
"""
Class for controlling NdYAG laser
"""
from PyQt5.QtCore import QThread
import serial
        
#########################################################################################
######################################NDYAG##############################################   

class Laser_NdYAG:
    def __init__(self, parameters={}):
        
        #defines the serial port for communication
        self.serial = serial.Serial(port='COM7',baudrate=9600,bytesize=8,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE)
        
        #set internal parameters
        self.make_clean_shot=parameters['make_clean_shot']
        self.cdelay=parameters['cdelay']
        self.nshots=parameters['n_shots']
        self.delay=parameters['delay']
        self.n_lin=parameters['n_lin']
        self.n_col=parameters['n_col']
        #self.int_time=parameters['integration_time']
        self.step=parameters['step']
        self.set_Qs(self.delay)     
    
    
    def check_state(self):
        return True
    
    
    def start_laser(self):
        """
        Starts the Laser.
        """
    
        print("Opening Shutter\n")
        self.open_shutter() #Opens the shutter

        print("Turning on the flashlamp\n")
        self.turn_on_lamp() #Turns on the flashlamp
    
    def getting_ready(self):
        
        #heating the cooler
        cooler=self.get_cooler_temperature()
        print(cooler)#Checks cooler temperature
        cooler = float(cooler)
        if cooler<326:
            #print("Heating")
            #print(str(cooler/32.6*100) + "%")
            return True, int(self.cooler_heating())
        
        else:
            return False, int(self.cooler_heating())
 

    def cooler_heating(self):
        
        cooler=float(self.get_cooler_temperature())
        #print(cooler)
        #print(str(cooler/32.6 *100) + "%")
        return cooler
    
    
    
    
    def pause(self):
        print("Turning off the flashlamp\n")
        self.turn_off_lamp() #Turns off the flashlamp

        print("Closing the shutter\n")
        self.close_shutter() #Closes the shutter
    
    
    def get_cooler_temperature(self):
        self.serial.read_all()
        self.serial.write(b'T3\r\n')
        QThread.msleep(500)
        m=self.serial.read_all()
        QThread.msleep(500)
        return(m.decode("utf-8").split("\r\n")[-1])[3:6]
                    
        
    def open_shutter(self):
        self.serial.write(b'SHC1\r\n')
        QThread.msleep(500)
        
    def close_shutter(self):
        self.serial.write(b'SHC0\r\n')
        QThread.msleep(500)

    def turn_on_lamp(self):
        self.serial.write(b'A\r\n')
        QThread.msleep(3000)

    def turn_off_lamp(self):
        self.serial.write(b'S\r\n')
        QThread.msleep(500)

    def get_Qs(self):
        self.serial.write(b'W\r\n')
        QThread.msleep(250)
        m=self.serial.read_all()
        QThread.msleep(250)
        return(m.decode("utf-8").split("\r\n")[-1])

    def set_Qs(self,delay):
        if 180<=delay<=500:
            delay=bytearray(str(int(delay)),"utf-8")
            self.serial.write(b'W' + delay + b'\r\n')
        else:
            print("Out of range. [180,500]")
            
    def set_parameters(self,parameters):
        delay = parameters['delay']
        
        
        if 180<=delay<=500:
            self.delay = delay
            delay=bytearray(str(int(delay)),"utf-8")
            self.serial.write(b'W' + delay + b'\r\n')
            
        else:
            print("Out of range. [180,500]")


    def single_shot(self):
        self.serial.write(b'OP\r\n')
        QThread.msleep(10) #250

    
    def shutter(self):
        self.serial.write(b'SHC\r\n')
        self.serial.flushOutput()
        QThread.msleep(200)
        m=self.serial.read_all()
        QThread.msleep(200)
        print(m.decode("utf-8").split("\r\n")[-1])
    
    
    ###############################################################
    ###############################################################
    
    
    def cooltemp(self):
        self.serial.write(b'CGT\r\n')
        QThread.msleep(500)
        m=self.serial.read_all()
        QThread.msleep(500)
        return(m.decode("utf-8").split("\r\n")[-1])

    def chargtemp(self):
        self.serial.write(b'CST\r\n')
        QThread.msleep(500)
        m=self.serial.read_all()
        QThread.msleep(500)
        return(m.decode("utf-8").split("\r\n")[-1])

    def alltemp(self):
        self.serial.write(b'T3\r\n')
        QThread.msleep(500)
        m=self.serial.read_all()
        QThread.msleep(500)
        return(m.decode("utf-8").split("\r\n")[-1])

    def coollevel(self):
        self.serial.write(b'LEV\r\n')
        QThread.msleep(500)
        m=self.serial.read_all()
        QThread.msleep(500)
        return(m.decode("utf-8").split("\r\n")[-1])

    def coolrate(self):
        self.serial.write(b'FLOW\r\n')
        QThread.msleep(500)
        m=self.serial.read_all()
        QThread.msleep(500)
        return(m.decode("utf-8").split("\r\n")[-1])
