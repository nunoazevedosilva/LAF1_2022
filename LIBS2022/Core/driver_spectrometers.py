# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 10:46:58 2021

@author: nunoa
"""

from Core.avaspec import *

import numpy as np
import matplotlib.pyplot as plt 
from PyQt5.QtCore import QThread

class Spectrometer_system:
    
    def __init__(self,ignore=None):
        """
        Start a spectrometer acquisition system

        """
        
        AVS_Init(0)
        
        n_dev = AVS_GetNrOfDevices()
        self.number_of_devices = n_dev
        
        
        
        a_pList = AVS_GetList()
        handle_list = []
        name_list =[]
        status_list = []
        
        for i in range(0,n_dev):
            print(a_pList[i].SerialNumber )
            if a_pList[i].SerialNumber == ignore:
                pass
                print('ignore',ignore,n_dev)
            else:
                name_list.append(a_pList[i].SerialNumber)
                status_list.append(a_pList[i].Status)
                handle_list.append(AVS_Activate(a_pList[i]))
                status_list.append(a_pList[i].Status)
        
        
        self.handle_list = handle_list
        self.status_list = status_list
        self.name_list = name_list
        
        wavelengths = []
        pixels_list=[]
        
        if ignore != None:
            n_dev = n_dev-1
            self.number_of_devices = n_dev
            
        for i in range(0,n_dev):
            print(i)
            current_config = AVS_GetParameter(self.handle_list[i])
            pixels = current_config.m_Detector_m_NrPixels
        
            
            current_wavelengths = []
            ret = AVS_GetLambda(handle_list[i])
            for pixel in range(pixels):
                current_wavelengths.append(ret[pixel])
                
            pixels_list.append(pixel)
            wavelengths.append(current_wavelengths)
        
        self.pixels_list = pixels_list
        self.config = None
        self.wavelengths = wavelengths
        self.last_spectrum = []
        self.current_measure = 1
        self.last_measure = 0
        
        print("Spectrometer system initialized - "+ str(n_dev)+ " devices")
        print(name_list)
    
    def gen_config_Master_and_Slaves(self, integration_time=50, delay_time=1, external_trigger = True):
        """
        Generate a configuration

        Returns
        -------
        None.

        """
        list_config = []
        
        for spec in range(0, 1):
            measconfig1 = MeasConfigType 
            measconfig1.m_StartPixel = 0 
            measconfig1.m_StopPixel = self.pixels_list[spec] - 1 
            
            measconfig1.m_IntegrationTime = integration_time
            measconfig1.m_IntegrationDelay = delay_time 
            measconfig1.m_NrAverages = 1 
            measconfig1.m_CorDynDark_m_Enable = 0 
            measconfig1.m_CorDynDark_m_ForgetPercentage = 100 
            measconfig1.m_Smoothing_m_SmoothPix = 0 
            measconfig1.m_Smoothing_m_SmoothModel = 0 
            measconfig1.m_SaturationDetection = 0 
            
            
            if external_trigger:
                if spec == 0:
                    measconfig1.m_Trigger_m_Mode = 1
                    measconfig1.m_Trigger_m_Source = 0
                    measconfig1.m_Trigger_m_SourceType = 0
                    
                else:
                    measconfig1.m_Trigger_m_Mode = 1 
                    measconfig1.m_Trigger_m_Source = 0 
                    measconfig1.m_Trigger_m_SourceType = 0 
                
            else:
                measconfig1.m_Trigger_m_Mode = 0 
                measconfig1.m_Trigger_m_Source = 0 
                measconfig1.m_Trigger_m_SourceType = 0
                
            measconfig1.m_Control_m_StrobeControl = 0 
            measconfig1.m_Control_m_LaserDelay = 0 
            measconfig1.m_Control_m_LaserWidth = 0 
            measconfig1.m_Control_m_LaserWaveLength = 0.0 
            measconfig1.m_Control_m_StoreToRam = 0
            
            print(measconfig1.m_Trigger_m_Source)
            
            list_config.append(measconfig1)
        print(list_config)
        print(list_config[0].m_Trigger_m_Source)
        
        for spec in range(1, self.number_of_devices):
            measconfig = MeasConfigType 
            measconfig.m_StartPixel = 0 
            measconfig.m_StopPixel = self.pixels_list[spec] - 1 
            
            measconfig.m_IntegrationTime = integration_time
            measconfig.m_IntegrationDelay = delay_time 
            measconfig.m_NrAverages = 1 
            measconfig.m_CorDynDark_m_Enable = 0 
            measconfig.m_CorDynDark_m_ForgetPercentage = 100 
            measconfig.m_Smoothing_m_SmoothPix = 0 
            measconfig.m_Smoothing_m_SmoothModel = 0 
            measconfig.m_SaturationDetection = 0 
            
            
            if external_trigger:
                if spec == 0:
                    measconfig.m_Trigger_m_Mode = 1 
                    measconfig.m_Trigger_m_Source = 0
                    measconfig.m_Trigger_m_SourceType = 0
                    
                else:
                    measconfig.m_Trigger_m_Mode = 1 
                    measconfig.m_Trigger_m_Source = 0
                    measconfig.m_Trigger_m_SourceType = 0 
                
            else:
                measconfig.m_Trigger_m_Mode = 0 
                measconfig.m_Trigger_m_Source = 0 
                measconfig.m_Trigger_m_SourceType = 0
                
            measconfig.m_Control_m_StrobeControl = 0 
            measconfig.m_Control_m_LaserDelay = 0 
            measconfig.m_Control_m_LaserWidth = 0 
            measconfig.m_Control_m_LaserWaveLength = 0.0 
            measconfig.m_Control_m_StoreToRam = 0
            
            print(measconfig.m_Trigger_m_Source)
            
            list_config.append(measconfig)
        print(list_config)
            
        print(" ------  -----")
        print(list_config[0].m_Trigger_m_Source)
        self.config = list_config
    
    
    def config_and_prepare_Master_and_Slaves(self, integration_time=50, delay_time=1, external_trigger = True):
        """
        Generate a configuration

        Returns
        -------
        None.

        """
        list_config = []
        

        for spec in range(0, self.number_of_devices):
            measconfig = MeasConfigType 
            measconfig.m_StartPixel = 0 
            measconfig.m_StopPixel = self.pixels_list[spec] - 1 
            
            measconfig.m_IntegrationTime = integration_time
            measconfig.m_IntegrationDelay = delay_time 
            measconfig.m_NrAverages = 1 
            measconfig.m_CorDynDark_m_Enable = 1 
            measconfig.m_CorDynDark_m_ForgetPercentage = 100 
            measconfig.m_Smoothing_m_SmoothPix = 0 
            measconfig.m_Smoothing_m_SmoothModel = 0 
            measconfig.m_SaturationDetection = 0 
            
            
            if external_trigger:
                if spec == 0:
                    measconfig.m_Trigger_m_Mode = 1 
                    measconfig.m_Trigger_m_Source = 0
                    measconfig.m_Trigger_m_SourceType = 0
                    
                else:
                    measconfig.m_Trigger_m_Mode = 1 
                    measconfig.m_Trigger_m_Source = 1
                    measconfig.m_Trigger_m_SourceType = 0 
                
            else:
                measconfig.m_Trigger_m_Mode = 0 
                measconfig.m_Trigger_m_Source = 0 
                measconfig.m_Trigger_m_SourceType = 0
                
            measconfig.m_Control_m_StrobeControl = 0 
            measconfig.m_Control_m_LaserDelay = 0 
            measconfig.m_Control_m_LaserWidth = 0 
            measconfig.m_Control_m_LaserWaveLength = 0.0 
            measconfig.m_Control_m_StoreToRam = 0
            
            
            
            current_handle = self.handle_list[spec]
            if spec == 0:
                AVS_SetSyncMode(current_handle, 1)
             
            AVS_PrepareMeasure(current_handle, measconfig)
            
            
            list_config.append(measconfig)

        self.config = list_config
     
    
    
    def gen_config(self, integration_time=50, delay_time=1, external_trigger = False):
        """
        Generate a configuration

        Returns
        -------
        None.

        """
        list_config = []
        
        for spec in range(0, self.number_of_devices):
            measconfig = MeasConfigType 
            measconfig.m_StartPixel = 0 
            measconfig.m_StopPixel = self.pixels_list[spec] - 1 
            
            measconfig.m_IntegrationTime = integration_time
            measconfig.m_IntegrationDelay = delay_time 
            measconfig.m_NrAverages = 1 
            measconfig.m_CorDynDark_m_Enable = 0 
            measconfig.m_CorDynDark_m_ForgetPercentage = 100 
            measconfig.m_Smoothing_m_SmoothPix = 0 
            measconfig.m_Smoothing_m_SmoothModel = 0 
            measconfig.m_SaturationDetection = 0 
            
            if external_trigger:
                measconfig.m_Trigger_m_Mode = 1 
                measconfig.m_Trigger_m_Source = 0 
                measconfig.m_Trigger_m_SourceType = 0 
                
            else:
                measconfig.m_Trigger_m_Mode = 0 
                measconfig.m_Trigger_m_Source = 0 
                measconfig.m_Trigger_m_SourceType = 0
                
            measconfig.m_Control_m_StrobeControl = 0 
            measconfig.m_Control_m_LaserDelay = 0 
            measconfig.m_Control_m_LaserWidth = 0 
            measconfig.m_Control_m_LaserWaveLength = 0.0 
            measconfig.m_Control_m_StoreToRam = 0
            
            
            list_config.append(measconfig)
            
        self.config = list_config
        
    def prepare_measure(self):
        for spec in range(0,self.number_of_devices):
            current_handle = self.handle_list[spec]
            AVS_PrepareMeasure(current_handle, self.config[spec])
            
    def prepare_measure_Master_and_Slaves(self):
        for spec in range(0,self.number_of_devices):
            current_handle = self.handle_list[spec]
            if spec == 0:
                None#AVS_SetSyncMode(current_handle, 1)
             
            AVS_PrepareMeasure(current_handle, self.config[spec])
            
    def stop_all_measures(self):
        for spec in range(0,self.number_of_devices):
            current_handle = self.handle_list[spec]
            AVS_StopMeasure(current_handle)
    
    def start_measure_Master_and_Slaves(self, scans):
        for spec in range(1, self.number_of_devices):
            current_handle = self.handle_list[spec]
            AVS_Measure(current_handle, 0, scans)
        
        current_handle = self.handle_list[0]
        AVS_Measure(current_handle, 0, scans)
        
    def is_data_ready(self):
        for spec in range(0, self.number_of_devices):
            current_handle = self.handle_list[spec]
            dataready = AVS_PollScan(current_handle)
            if not dataready:
                print("Spectrometer "+str(spec)+" - Data not acquired")
                return False
            else:
                print("Spectrometer "+str(spec)+" - Data acquired")
        return True
        
           
    def measure(self, scans):
        for spec in range(0, self.number_of_devices):
            current_handle = self.handle_list[spec]
            AVS_Measure(current_handle, 0, scans)
            
            QThread.msleep(100)

            dataready = AVS_PollScan(current_handle)
            
            if not dataready:
                print("Data not acquired")
                
    def start_LIBS_mode_old(self, integration_time=50, delay_time=1, scans=1):
        self.gen_config_Master_and_Slaves(integration_time=integration_time, delay_time=delay_time)
        self.prepare_measure_Master_and_Slaves()
        self.start_measure_Master_and_Slaves(scans=scans)
        print('LIBS mode of Spectrometers Ready and waiting')

    def start_LIBS_mode(self, integration_time=50, delay_time=1, scans=1):
        self.config_and_prepare_Master_and_Slaves(integration_time=integration_time, delay_time=delay_time)
        self.start_measure_Master_and_Slaves(scans=scans)
        print('LIBS mode of Spectrometers Ready and waiting')
        
    def get_data(self):
        """
        not_ready = self.is_ready()
        while not_ready:
            #restart ports
            not_ready = self.is_ready()
        """
        timestamp = 0

        spectrum = []
        
        for spec in range(0, self.number_of_devices):
            spectraldata = []
            current_handle = self.handle_list[spec]
            ret = AVS_GetScopeData(current_handle)
            timestamp = ret[0]
            for i,pix in enumerate(self.wavelengths[spec]):
                spectraldata.append(ret[1][i])
                
            spectrum.append(spectraldata)
            #time.sleep(1500/1000)
        
        self.last_spectrum = spectrum
        self.last_measure = self.current_measure
        self.current_measure += 1
        
    
    def plot_data(self):
        self.get_data()
        last_spectrum = self.last_spectrum
        #plt.subplots()
        self.wavel=[]
        self.intens=[]
        for spec in range(0, self.number_of_devices):
            #plt.plot(self.wavelengths[spec],last_spectrum[spec],'-')
            self.wavel.append(self.wavelengths[spec])
            self.intens.append(last_spectrum[spec])
        return self.wavel, self.intens

        
        
    
    def save_data(self, folder, filename='auto'):
        
        """
        Save data to file
        """
        
        paths_list = []
        if filename == 'auto':
            shot = str(self.last_measure-1).zfill(4)
            for spec in range(0,self.number_of_devices):
                current_name = self.name_list[spec].decode('utf-8')
                filename = current_name + '_'+shot+'_'+current_name+'.TXT'
                path = folder +'//'+ filename
                paths_list.append(path)
            
        else:
            shot = str(self.last_measure-1).zfill(4)
            for spec in range(0,self.number_of_devices):
                current_name = self.name_list[spec].decode('utf-8')
                
                filename = current_name + '_'+shot+'_'+current_name+'.TXT'
                path = folder +'//'+ filename
                paths_list.append(path)
        
        for spec in range(0,self.number_of_devices):
            current_path = paths_list[spec]
            current_file = open(current_path, "w")
            sp = np.array(self.last_spectrum[spec])
            wl = np.array(self.wavelengths[spec])
            z = np.zeros(wl.shape)

            line_0 = ' '
            current_file.write(line_0+'\n')
            line_1 = 'Integration time [ms]:'+'\t'+str(self.config[spec].m_IntegrationTime)
            current_file.write(line_1+'\n')
            line_2 = 'Averaging Nr. [scans]:'+str(self.config[spec].m_NrAverages)
            current_file.write(line_2+'\n')
            line_3 = 'Smoothing Nr. [pixels]:'+str(self.config[spec].m_Smoothing_m_SmoothPix)
            current_file.write(line_3+'\n')
            line_4 = 'Data measured with spectrometer [name]:'+str(self.name_list[spec])
            current_file.write(line_4+'\n')
            line_5 = 'Wave\t;Sample\t;Dark\t;Reference\t;Scope\t'
            current_file.write(line_5+'\n')
            line_6 = '[nm]\t;[counts]\t;[counts]\t;[counts]\t'
            current_file.write(line_6+'\n')
            line_7 = ' '
            current_file.write(line_7+'\n')
            
            for i in range(0,len(wl)):
                wave_str = str(wl[i]).replace('.',',')+';\t'
                sample_str = str(sp[i]).replace('.',',')+';\t'
                dark_str = str(z[i]).replace('.',',')+';\t'
                ref_str = str(z[i]).replace('.',',')+'\n'
                current_line = wave_str + sample_str + dark_str + ref_str
                current_file.write(current_line)
            
            current_file.close()


    def save_data_clean_shot(self, folder, filename='auto'):
        
        """
        Save data to file
        """
        
        paths_list = []
       
        if filename == 'auto':
            shot = str(self.last_measure-1).zfill(4)
            for spec in range(0,self.number_of_devices):
                current_name = self.name_list[spec].decode('utf-8')
                filename = current_name + '_0000_' +current_name+'.TXT'
                path = folder +'//'+ filename
                paths_list.append(path)
           
        else:
            shot = str(self.last_measure-1).zfill(4)
            for spec in range(0,self.number_of_devices):
                current_name = self.name_list[spec].decode('utf-8')
                
                filename = current_name + '_0000_'+current_name+'.TXT'
                path = folder +'//'+ filename
                paths_list.append(path)
        
        for spec in range(0,self.number_of_devices):
            current_path = paths_list[spec]
            current_file = open(current_path, "w")
            sp = np.array(self.last_spectrum[spec])
            wl = np.array(self.wavelengths[spec])
            z = np.zeros(wl.shape)

            line_0 = ' '
            current_file.write(line_0+'\n')
            line_1 = 'Integration time [ms]:'+'\t'+str(self.config[spec].m_IntegrationTime)
            current_file.write(line_1+'\n')
            line_2 = 'Averaging Nr. [scans]:'+str(self.config[spec].m_NrAverages)
            current_file.write(line_2+'\n')
            line_3 = 'Smoothing Nr. [pixels]:'+str(self.config[spec].m_Smoothing_m_SmoothPix)
            current_file.write(line_3+'\n')
            line_4 = 'Data measured with spectrometer [name]:'+str(self.name_list[spec])
            current_file.write(line_4+'\n')
            line_5 = 'Wave\t;Sample\t;Dark\t;Reference\t;Scope\t'
            current_file.write(line_5+'\n')
            line_6 = '[nm]\t;[counts]\t;[counts]\t;[counts]\t'
            current_file.write(line_6+'\n')
            line_7 = ' '
            current_file.write(line_7+'\n')
            
            for i in range(0,len(wl)):
                wave_str = str(wl[i]).replace('.',',')+';\t'
                sample_str = str(sp[i]).replace('.',',')+';\t'
                dark_str = str(z[i]).replace('.',',')+';\t'
                ref_str = str(z[i]).replace('.',',')+'\n'
                current_line = wave_str + sample_str + dark_str + ref_str
                current_file.write(current_line)
            
            current_file.close()        

            
    def save_data_map(self, x_pos,y_pos, folder, shot_number, filename='auto'):
        
        """
        Save data to file
        """
        
        paths_list = []
        shot = str(shot_number).zfill(4)
        if filename == 'auto':
            
            for spec in range(0,self.number_of_devices):
                current_name = self.name_list[spec].decode('utf-8')
                filename = current_name + '_'+ shot+'_'+current_name+'.TXT'
                path = folder +'//'+ filename
                paths_list.append(path)
            
        else:
      
            for spec in range(0,self.number_of_devices):
                current_name = self.name_list[spec].decode('utf-8')
                
                filename = current_name + '_'+shot+'_'+current_name+'.TXT'
                path = folder +'//'+ filename
                paths_list.append(path)
        
        for spec in range(0,self.number_of_devices):
            current_path = paths_list[spec]
            current_file = open(current_path, "w")
            sp = np.array(self.last_spectrum[spec])
            wl = np.array(self.wavelengths[spec])
            z = np.zeros(wl.shape)
            
            #if y_pos != 0:                         #corrige a direção do y nos mapas
             #   y_pos = (-1)*y_pos
                

            line_0 = str(y_pos)+'\t'+str(x_pos)    #axis1=y axis2=x
            #line_0 = str(x_pos)+'\t'+str(y_pos)
            #current_file.write(line_0+'\n')
            line_1 = 'Integration time [ms]:'+'\t'+str(self.config[spec].m_IntegrationTime)
            #current_file.write(line_1+'\n')
            line_2 = 'Averaging Nr. [scans]:'+str(self.config[spec].m_NrAverages)
            #current_file.write(line_2+'\n')
            line_3 = 'Smoothing Nr. [pixels]:'+str(self.config[spec].m_Smoothing_m_SmoothPix)
            #current_file.write(line_3+'\n')
            line_4 = 'Data measured with spectrometer [name]:'+str(self.name_list[spec])
            #current_file.write(line_4+'\n')
            line_5 = 'Wave\t;Sample\t;Dark\t;Reference\t;Scope\t'
            #current_file.write(line_5+'\n')
            line_6 = '[nm]\t;[counts]\t;[counts]\t;[counts]\t'
            #current_file.write(line_6+'\n')
            line_7 = ' '
            current_file.write(line_0 +'\n'+ line_1+'\n'+line_2+'\n'+line_3+'\n'+line_4+'\n'+line_5+'\n'+line_6 +'\n'+line_7+'\n')
            
            for i in range(0,len(wl)):
                wave_str = str(wl[i]).replace('.',',')+';\t'
                sample_str = str(sp[i]).replace('.',',')+';\t'
                dark_str = str(z[i]).replace('.',',')+';\t'
                ref_str = str(z[i]).replace('.',',')+'\n'
                current_line = wave_str + sample_str + dark_str + ref_str
                current_file.write(current_line)
            
            current_file.close()
            
###########################-------------------------------------------------------###################################
#####################################################################################################################

            
class Spectrometer_system_demo:
    
    def __init__(self):
        """
        Start a spectrometer acquisition system

        Returns
        -------
        None.

        """
        
        AVS_Init(0)
        
        n_dev = AVS_GetNrOfDevices()
        self.number_of_devices = n_dev
        
        a_pList = AVS_GetList()
        handle_list = []
        name_list =[]
        status_list = []
        
        for i in range(0,n_dev):
            name_list.append(a_pList[i].SerialNumber)
            status_list.append(a_pList[i].Status)
            handle_list.append(AVS_Activate(a_pList[i]))
            status_list.append(a_pList[i].Status)
        
        self.handle_list = handle_list
        self.status_list = status_list
        self.name_list = name_list
        
        wavelengths = []
        pixels_list=[]
        
        for i in range(0,n_dev):
            current_config = AVS_GetParameter(self.handle_list[i])
            pixels = current_config.m_Detector_m_NrPixels
        
            
            current_wavelengths = []
            ret = AVS_GetLambda(handle_list[i])
            for pixel in range(pixels):
                current_wavelengths.append(ret[pixel])
                
            pixels_list.append(pixel)
            wavelengths.append(current_wavelengths)
        
        self.pixels_list = pixels_list
        self.config = None
        self.wavelengths = wavelengths
        self.last_spectrum = []
        self.current_measure = 1
        self.last_measure = 0
        
        print("Spectrometer system initialized - "+ str(n_dev)+ " devices")
        print(name_list)
    
    def gen_config_Master_and_Slaves(self, integration_time=50, delay_time=1, external_trigger = True):
        pass
    
    
    def config_and_prepare_Master_and_Slaves(self, integration_time=50, delay_time=1, external_trigger = True):
        pass
     
    
    
    def gen_config(self, integration_time=50, delay_time=1, external_trigger = False):
        pass
        
    def prepare_measure(self):
        pass
            
    def prepare_measure_Master_and_Slaves(self):
        pass
            
    def stop_all_measures(self):
        pass
    
    def start_measure_Master_and_Slaves(self, scans):
        pass
        
    def is_data_ready(self):
        
        return True
        
           
    def measure(self, scans):
        pass
                
    def start_LIBS_mode_old(self, integration_time=50, delay_time=1, scans=1):
        pass

    def start_LIBS_mode(self, integration_time=50, delay_time=1, scans=1):
        pass
        
    def get_data(self):
        timestamp = 0

        spectrum = [np.random.rand(100),np.random.rand(100)]
        
        self.last_spectrum = spectrum
        self.last_measure = self.current_measure
        self.current_measure += 1
        
    
    def plot_data(self):
        self.get_data()
        last_spectrum = self.last_spectrum
        #plt.subplots()
        self.wavel=[]
        self.intens=[]
        for spec in range(0, len(self.last_spectrum)):
            #plt.plot(self.wavelengths[spec],last_spectrum[spec],'-')
            self.wavel.append(150+np.arange(0,len(self.last_spectrum[spec])))
            self.intens.append(last_spectrum[spec])
        return self.wavel, self.intens

        
        
    
    def save_data(self, folder, filename='auto'):
        
        pass


    def save_data_clean_shot(self, folder, filename='auto'):
        
        pass
            
    def save_data_map(self, x_pos,y_pos, folder, shot_number, filename='auto'):
        
        pass
        
                
