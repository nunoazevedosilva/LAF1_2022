import serial
import time
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from Laser import *
from Stages import *
from LIBS import *
import os
import config


def addzero(number): #fartei-me de fazer ifs para isto
    if number<10:
        return "000"+str(number)
    elif number<100:
        return "00"+str(number)
    elif number<1000:
        return "0"+str(number)
    else:
        return str(number)

def enter(): #function to advance using enter and manually warning for errors
    error=False
    inp="0"

    while inp!="Error" and inp!="":
        inp=input("Press Enter to shoot, input Error in case of AvaSoft error: ")
        print("\n")
    if inp=="Error":
        error=True
        return error
        
    if inp=="":

        return error


#Selecting the folder that will contain the data
folder = r'C:\Users\LIBS\Desktop\Teste1'

#configuration


def config ():
    cshot=input('Clean Shot required: Yes or No? )')
    c_delay = None
    
    if cshot=='Yes':
        c_delay=int(input('Clean Shot Q-Switch Delay = '))
    
    nshots=int(input('Number of Shots per spot = '))

    delays = int(input ('Q-Switch Delay = '))

    n_lin = int(input ('# lines ='))
    n_col = int(input ('# columns ='))

    step = float(input ('Step =' ))

    coor = coordinates(n_lin, n_col ,step)

    return [c_delay, n_shots, delays, coor]




#Checking if a folder was selected, if not it won't start the program
if folder!="":

    #Saves the number of files in the folder to check later if new files are added
    size=len(os.listdir(folder))
    print(size)


    #RS-232 connections
    Dualstage = serial.Serial("COM1", baudrate=9600,timeout=1,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    MyLaser=serial.Serial(port='COM5',baudrate=9600,bytesize=8,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE)
    MySpec=serial.Serial(port='' ,baudrate=9600,bytesize=8,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE)      #complete

    S=Driver(Stage(1),Stage(2),Dualstage)
    L=Laser(MyLaser)
    Sp=Spectrometer(MySpec)   #verify



    start= starting(S,L) 

    print(start)

    d=0 #variable to run through the delays
    c=0 #variable to run through the coordinates
    nerror=0 # variable to save the number of errors that happen during the analysis
    v=[] #list for saving the used delay or errors
    t1=time.time()

    while d<(len(delays)):

        #Go to
        x= start[0]+coor[c][0]*step
        y= start[1]+coor[c][1]*step
        print("Moving to (" + str(x) + "," + str(y) + ")\n")
        
        S.posAxy(round(x,3),round(y,3))
        c+=1
        e=False #no error stance
        
        for j in range(nshots+1):
            if j==0:
                L.setQs(cdelay)
                print("Clean shot. Ready?")
                time.sleep(1)
                
                L.singleshot()

                time.sleep(3)
                print(len(os.listdir(folder)))
                print(size)


# Check for errors, set file placeholders, set an error stance
                v,nerror,e = errorcheck(folder,v,nerror,e,size)

                size=len(os.listdir(folder))
                L.setQs(delays[d])
                print(L.Qs())
                
            else:
                print("Shot " + str(j) + ". Ready?")

                time.sleep(1)
                
                L.singleshot()
                time.sleep(3)
                print(len(os.listdir(folder)))
                print(size)

                v,nerror,e = errorcheck(folder,v,nerror,e,size)
                        
                size=len(os.listdir(folder))
                
            
            if e:
                
                nerror+=1
                files=os.listdir(folder)
                last=int(files[-1].split("_")[-1][:4])
                deleted=0
                for k in range(d*(1+nshots)+1,(d+1)*(1+nshots)+1):
                    num=str(k)+".Raw8"
                    for file in files:
                        if num in file:
                            os.remove(folder + "//" + file)
                            deleted+=1
                print(str(deleted) + " files were deleted")
                size=len(os.listdir(folder))
                d+=-1
                break
        
        
        if not e:
            v.append(delays[d])
            d+=1


    hibernating(S,L)

    t2=time.time()
    t=t2-t1


    #Saving information
    f=open(folder+"\\Data.txt","w")
    text="Sample: " + folder.split("/")[-1] + "\n"
    text+="\nStep = " + str(step) + " mm\t\t Number of shots per spot = clean shot + " + str(nshots) + "\n"
    text+="\nTime taken = " + str(t) + " s\n\n"
    text+="Clean shot: " + str(cdelay) + " us\n\n"
    text+="Coordenates\t\tQ-switch Delay (us)\n"
    for i in range(len(v)):
        x= start[0]+coor[i][0]*step
        y=start[1]+coor[i][1]*step
        text+="(" + str(x) + "," + str(y) +")" + "\t\t\t" + str(v[i]) + "\n"

    f.write(text)
        
    f.close()


    
    
    
    
    
    


    
