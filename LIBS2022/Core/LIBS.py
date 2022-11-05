import os
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox

def addzero(number): #fartei-me de fazer ifs para isto
    if number<10:
        return "000"+str(number)
    elif number<100:
        return "00"+str(number)
    elif number<1000:
        return "0"+str(number)
    else:
        return str(number)

def starting(S,L):
    print("Starting the stages\n")
    S.on() #Turns the stages on

    #messagebox.showinfo(title="Select starting point", message="Move the stages to the starting position")

    starting = S.fposAxy()

    start =(float(starting[0]),float(starting[1]))
    
    print("Opening Shutter\n")
    L.openS() #Opens the shutter

    print("Turning on the flashlamp\n")
    L.onLamp() #Turns on the flashlamp

    print(L.alltemp()[3:6])
    cooler=float(L.alltemp()[3:6])/10 #Checks cooler temperature

    if cooler<32.6:
        print("Heating")
        print(str(cooler/32.6*100) + "%")
        while cooler<32.6:
            if cooler!=float(L.alltemp()[3:6])/10:
                print(L.alltemp()[3:6])
                cooler=float(L.alltemp()[3:6])/10
                print(str(cooler/32.6 *100) + "%")
    return start

def hibernating(S,L):
    print("Turning off the flashlamp\n")
    L.offLamp() #Turns off the flashlamp

    print("Closing the shutter\n")
    L.closeS() #Closes the shutter

    print("Turning off the stages")
    S.off() #Turns the stages off

def errorcheck(folder,v,nerror,e,size):
    if len(os.listdir(folder))!=size+8:
        #messagebox.showinfo(title="Error in Avasoft!", message="Reset Avasoft")
        nerror+=1
        files=os.listdir(folder)
                
        if "1703272U8_0001.Raw8" not in files:
            f=open(folder+"\\1703272U8_0001.Raw8","w")
            f.close()
            f=open(folder+"\\1703273U8_0001.Raw8","w")
            f.close()
            f=open(folder+"\\1703274U8_0001.Raw8","w")
            f.close()
            f=open(folder+"\\1703275U8_0001.Raw8","w")
            f.close()
            f=open(folder+"\\1703276U8_0001.Raw8","w")
            f.close()
            f=open(folder+"\\1703277U8_0001.Raw8","w")
            f.close()
            f=open(folder+"\\1703278U8_0001.Raw8","w")
            f.close()
            f=open(folder+"\\1703279U8_0001.Raw8","w")
            f.close()
            v.append("Error")
            e=True
                    
                        
        else:
            last=files[-1]
                    
            linkl=last.split("_")
            n=int(linkl[1][:4])
                        
            f=open(folder+"\\1703272U8_" + addzero(n+1) + ".Raw8","w")
            f.close()
            f=open(folder+"\\1703273U8_" + addzero(n+1) + ".Raw8","w")
            f.close()
            f=open(folder+"\\1703274U8_" + addzero(n+1) + ".Raw8","w")
            f.close()
            f=open(folder+"\\1703275U8_" + addzero(n+1) + ".Raw8","w")
            f.close()
            f=open(folder+"\\1703276U8_" + addzero(n+1) + ".Raw8","w")
            f.close()
            f=open(folder+"\\1703277U8_" + addzero(n+1) + ".Raw8","w")
            f.close()
            f=open(folder+"\\1703278U8_" + addzero(n+1) + ".Raw8","w")
            f.close()
            f=open(folder+"\\1703279U8_" + addzero(n+1) + ".Raw8","w")
            f.close()

            v.append("Error")
            e=True
    return v,nerror,e      
