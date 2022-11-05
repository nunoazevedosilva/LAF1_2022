
import time
import serial



class Laser:

    def __init__(self,serial):
        self.serial=serial

    def shutter(self):
        self.serial.write(b'SHC\r\n')
        self.serial.flushOutput()
        time.sleep(0.2)
        m=self.serial.read_all()
        time.sleep(0.2)
        print(m.decode("utf-8").split("\r\n")[-1])
        
    def openS(self):
        self.serial.write(b'SHC1\r\n')
        time.sleep(0.2)
        
    def closeS(self):
        self.serial.write(b'SHC0\r\n')
        time.sleep(0.2)

    def onLamp(self):
        self.serial.write(b'A\r\n')
        time.sleep(3)

    def offLamp(self):
        self.serial.write(b'S\r\n')
        time.sleep(0.2)

    def Qs(self):
        self.serial.write(b'W\r\n')
        time.sleep(0.5)
        m=self.serial.read_all()
        time.sleep(0.5)
        return(m.decode("utf-8").split("\r\n")[-1])

    def setQs(self,delay):
        if 180<=delay<=500:
            delay=bytearray(str(int(delay)),"utf-8")
            self.serial.write(b'W' + delay + b'\r\n')
        else:
            print("Out of range. [180,500]")

    def singleshot(self):
        self.serial.write(b'OP\r\n')
        
        time.sleep(0.5)

    def cooltemp(self):
        self.serial.write(b'CGT\r\n')
        time.sleep(0.5)
        m=self.serial.read_all()
        time.sleep(0.5)
        return(m.decode("utf-8").split("\r\n")[-1])

    def chargtemp(self):
        self.serial.write(b'CST\r\n')
        time.sleep(0.5)
        m=self.serial.read_all()
        time.sleep(0.5)
        return(m.decode("utf-8").split("\r\n")[-1])

    def alltemp(self):
        self.serial.write(b'T3\r\n')
        time.sleep(0.5)
        m=self.serial.read_all()
        time.sleep(0.5)
        return(m.decode("utf-8").split("\r\n")[-1])

    def coollevel(self):
        self.serial.write(b'LEV\r\n')
        time.sleep(0.2)
        m=self.serial.read_all()
        time.sleep(0.2)
        return(m.decode("utf-8").split("\r\n")[-1])

    def coolrate(self):
        self.serial.write(b'FLOW\r\n')
        time.sleep(0.2)
        m=self.serial.read_all()
        time.sleep(0.2)
        return(m.decode("utf-8").split("\r\n")[-1])
#L=Laser(MyLaser)

