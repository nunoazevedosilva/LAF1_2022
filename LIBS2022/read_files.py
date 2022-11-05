import os
import numpy as np

def read_data(filename):
    

    
    fl=open(filename,'r')
    wave=[]
    sample=[]
    dark=[]
    reference=[]
    
    #skips header
    pos = fl.readline()
    position = [float(pos.split('\t')[0]),float(pos.split('\t')[0])]
    for i in range(1,8):
        if i !=1:
            fl.readline()
        else:
            line = fl.readline()
            try:
                integration_time = float(line.split(':')[1][:-1].split(' ')[-1].replace(',','.'))
            except:
                integration_time = None
    
    line=fl.readline()
    
    #for all lines now
    while len(line)>1:
        #print "nl" + line
        line=line.replace(",",".")
        data=line.split(";")
        wave.append(float(data[0]))
        sample.append(float(data[1]))
        dark.append(float(data[2]))
        reference.append(float(data[3]))
        line=fl.readline()
    
    fl.close()
        
    return np.array(wave),np.array(sample),np.array(position)


def read_libs_data(folder,ignore=None):
    

    #find if file has multiple channels
    
    list_folder = np.array([np.array([d.split("_")[0],d.split("_")[1],
                                d.split("_")[2]]) for d in os.listdir(folder) if d.endswith(".TXT") or d.endswith(".txt")])
    
    shots = np.unique(list_folder[:,1])
    list_of_signals = []
    list_of_positions = []
    
    for i in range(0, len(shots)):
        
        shot_number = shots[i]
        if shot_number != ignore:
            if len(np.where(np.unique(list_folder[:,1])==shot_number)[0])!=0:
                multi_channel = True
            
            wavelength = []
            spectrum = []
            dark = []
            reference = []
            spectrometer_labels = []
            integration_time = None
            
            for spectrometer in np.unique(list_folder[:,0]):
                #current filename to read
                current_file = folder + spectrometer +"_"+ shot_number+"_"+  spectrometer + ".TXT"
                
#                 try:

                #read data from the current file
                wavelength_current, spectrum_current, position = read_data(current_file)

                #append to data lists
                wavelength.append(wavelength_current)
                spectrum.append(spectrum_current)
                
#                 #if for some reason the file does not exist
#                 except:
#                     print("Warning - Skipped file " + current_file + ", does not exists" )
                    
            list_of_positions.append(position)
            list_of_signals.append(np.array(spectrum))
    
    return np.array(wavelength), np.array(list_of_signals), np.array(list_of_positions)
    