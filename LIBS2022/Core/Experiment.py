import serial
import time

from Core.Laser import *
from Core.Stages import *
from Core.LIBS import *
from Core.driver_spectrometers import *

import os

from PyQt5.QtWidgets import QMessageBox, QProgressBar
from PyQt5.QtCore import QThread
from multiprocessing import Lock
import shutil
import numpy as np


class Experiment:
    
    def __init__(self, system='NdYAG', parameters={}, ignore_spectrometer=None):
        """
        Starts a new experiment.
    
        current_position, tuple

        """
        #position
        self.current_position=(0, 0)
        
        #set the system (NdYAG, Fiber, Demo)
        self.system=system
        
        #store the parameters
        self.parameters=parameters
        
        #Initialize the stages, laser and spectrometer
        self.stage_system=Stage_System(system=system)
        self.laser_system=Laser_System(system=system, parameters=parameters)
        
        if system!= 'Demo':
            self.spec_system = Spectrometer_system(ignore=ignore_spectrometer)
        else:
            self.spec_system = Spectrometer_system_demo()
            
            
    def set_system_parameters (self, parameters):
        
        self.parameters=parameters
        
        #Initialize the stages, laser and spectrometer
        self.stage_system=Stage_System(system=self.system)
        self.laser_system=Laser_System(system=self.system, parameters=parameters)
        self.spec_system = Spectrometer_system()



        
    
    def set_pos(self, x, y):
    
        print("Moving to (" + str(x) + "," + str(y) + ")\n")
        self.stage_system.move_to(round(x,3),round(y,3))
        

    def start_stages(self):
        self.stage_system.turn_on()        #Turns the stages on
        

        temp_pos = self.stage_system.go_home()[1]
        
        #self.current_position=(0, 0)

        self.current_position =(float(temp_pos[0]),float(temp_pos[1]))
    
    def start_laser(self):
        self.laser_system.start_laser()

    def set_globalvar(self):
        global_var =1  
        
    def start_spectrometer(self, integration_time=1.05, delay_time = 1):
        self.spec_system.start_LIBS_mode(integration_time=integration_time, delay_time=delay_time)

    def pause_system(self):
        self.laser_system.pause()
        
    def hibernate(self):
       
        self.laser_system.pause()
        
        #self.stage_system.go_home()
        QThread.msleep(10000)
        

        
        self.stage_system.turn_off() #Turns the stages off
        
##########################################################################

    def generate_coordinate(self, lines, columns, step):
        start=(0,0)
        coor=[]
        for i in range(lines):
            if i%2==0:
                add=-1*step
            else:
                add=step
            for j in range(columns):
                if i==0 and j==0:
                    coor.append(start)
                elif j==0:
                    x=round(coor[-1][0]+ step, 2)
                    y=coor[-1][1]
                    coor.append((x,y))
                else:
                    x=coor[-1][0]
                    y=round (coor[-1][1] + add, 2)
                    coor.append((x,y))
        print(coor)
        return coor
        

    def generate_coordinate_pellets(self, rep, len_QS , step, radius = 6):
        lines, columns = int((2*radius/float(step))+1), int((2*radius/float(step))+1)

        coor = self.generate_coordinate(lines, columns, step)
        coor = np.subtract(coor,np.array([radius,-radius]))
        norm = np.array([np.linalg.norm(c) for c in coor])
        coor = coor[norm<=0.85*radius]
        
        if rep*len_QS>len(coor):
            print('Number of spots exceed the len of possible coordinates')
        
        coor=coor.tolist()
        print('selected coordinates'+str(coor))
        print(len(coor))
        return coor
    
    
    def save_experiment_parameters(self, sample_folder, experiment_mode, time_taken = 0, error = False, type_error = [], error_shot_n = [], error_shot_pos = [], resume = False):
        log_folder = "C:\\LIBS_logs\\" + self.system
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        time_info = time.localtime()
        
        sample = sample_folder.split("\\")[-1].split("//")[-1].split("/")[-1]
    
        filename = "LIBS_log_" + str(time_info[0]) + "-" + str(time_info[1]) + "-" + str(time_info[2]) + "_" + str(time_info[3]) + "." + str(time_info[4]) + "." + str(time_info[5])
        log_file = open(log_folder + "\\" + filename, "w")
        log_file.write(experiment_mode + " on sample " + sample + "\n")
        
        if resume:
            log_file.write("Resume\n")
        else:
            log_file.write("\n\n")
            
        log_file.write("Saved at " + sample_folder + "\n\n")
        
        if time_taken:
            log_file.write("Total time: " + str(time_taken) + " s\n\n")
        else:
            log_file.write("\n\n\n")
            
        
        """
        if experiment_mode = "Map":
            
            log_file.write(self.parameters['scans'] + "x" + self.parameters['n_lin'] +" points\n")
            log_file.write("Step size: " + self.parameters['step (mm)'] + "x" + self.parameters['step (mm)'] +" mm^2\n")
        """
        
        log_file.write("Parameters:\n")
        
        
        for i in self.parameters:
            log_file.write(i + ":" + str(self.parameters[i]) + "\n")
            
        
        if error:
            
            log_file.write("\nObservations:\n")
            for j in range(len(type_error)):
                
                log_file.write("Error " + type_error[j] + "\n")
                log_file.write("At: " +  str(error_shot_pos[j][0]) + "," + str(error_shot_pos[j][1]) + "\n")
                log_file.write("Shot number: " + str(error_shot_n[j]) + "\n")
                
        log_file.close()
        
###########################################################################################
              
    def single_shot(self, folder, cooler_temperature = [], shot_progress = [], x_shared =[] , y_shared=[], lock= Lock(),end_bool=[1]):

        
        shot_prog=0
        if self.parameters['make_clean_shot']==True:
            total=2
        else:
            total=1
              
        self.start_stages()
        
        #QMessageBox.about(parent, "Warning", "Inappropriate mapping analysis selection")     
        #messagebox.showwarning(title='Warning', message='Please align the sample!')

        self.start_laser()
        
        lock.acquire()
        laser_not_ready, cooler_temp = self.laser_system.getting_ready()
        while laser_not_ready:
            laser_not_ready, cooler_temp = self.laser_system.getting_ready()
        lock.release()
      
        if self.parameters['make_clean_shot']==True:
            print("Clean shot. Ready?")
            self.start_spectrometer()
            self.clean_shot(folder)
            shot_prog+=1
            
            lock.acquire()
            shot_prog=(shot_prog/total)*100
            lock.release()

            QThread.msleep(300)
                
        self.start_spectrometer()
        QThread.msleep(300)

        print("Single shot...",end='\t')
        self.laser_system.single_shot()
        shot_prog+=1

        lock.acquire()
        x,y = self.spec_system.plot_data()
        
        x_shared.append(x)
        y_shared.append(y)
        
        lock.release()
        
        QThread.msleep(300)
        print('done.')
        
        self.spec_system.save_data(folder=folder)
        self.hibernate()
        end_bool.append(0)
        
        return x_shared,y_shared 
        
        
    def single_shot1(self, folder, cooler_temperature = 0, shot_progress = 0, x_shared =[] , y_shared=[], lock= Lock()):
        print('Oi')
        shot_prog=0
        if self.parameters['make_clean_shot']==True:
            total=2
        else:
            total=1
              
        self.start_stages()
        
        #QMessageBox.about(parent, "Warning", "Inappropriate mapping analysis selection")     
        #messagebox.showwarning(title='Warning', message='Please align the sample!')

        self.start_laser()
        
        lock.acquire()
        laser_not_ready, cooler_temperature = self.laser_system.getting_ready()
        while laser_not_ready:
            laser_not_ready, cooler_temperature = self.laser_system.getting_ready()
        lock.release()
      
        if self.parameters['make_clean_shot']==True:
            print("Clean shot. Ready?")
            self.start_spectrometer()
            self.clean_shot(folder)
            shot_prog+=1
            
            lock.acquire()
            shot_progress=(shot_prog/total)*100
            lock.release()

            QThread.msleep(250)
                
        self.start_spectrometer()
        QThread.msleep(250)

        print("Single shot...",end='\t')
        self.laser_system.single_shot()
        shot_prog+=1

        lock.acquire()
        x_shared, y_shared = self.spec_system.plot_data()
        lock.release()
        
        QThread.msleep(250)
        print('done.')
        
        self.spec_system.save_data(folder=folder)
        self.hibernate()
        
        return x,y 
        
        #self.GUI_plot(graphic,peak, x, y)
        #meas_progressBar.setValue((shot_prog/total)*100)
            
    
    
    def SCRIPT_plot(self,peak,x,y):  

        if peak!=None:
            
            x_comp=np.ndarray.flatten(np.array(x))
            y_comp=np.ndarray.flatten(np.array(y))
            #x_comp=[np.concatenate(x_comp, i for i in x)]
            index = (np.abs(x_comp - float(peak))).argmin()
            
            x_peak=[x_comp[i] for i in range(max(index-10, 0), min(index+10, x_comp.size))]
            y_peak=[y_comp[j] for j in range(max(index-10, 0), min(index+10, y_comp.size))]
            
            plt.plot(x, y)
            plt.plot(x_peak, y_peak)
            plt.show()
        
        else:
            plt.plot(x, y)
            plt.show()


    def GUI_plot(self, graphic, peak,x,y):
        
        if peak!=None:
            
            x_comp=np.ndarray.flatten(np.array(x))
            y_comp=np.ndarray.flatten(np.array(y))
            #x_comp=[np.concatenate(x_comp, i for i in x)]
            index = (np.abs(x_comp - float(peak))).argmin()
            
            x_peak=[x_comp[i] for i in range(max(index-10, 0), min(index+10, x_comp.size))]
            y_peak=[y_comp[j] for j in range(max(index-10, 0), min(index+10, y_comp.size))]
            graphic.update_figure(x, y, x_peak, y_peak, element)
        
        else:
            graphic.update_figure(x, y)

        
        

    
    def multi_shot(self, folder, resume=False, shot_number=False, integration_time = 1.05, spec_delay_time=1):   #resume - coordenada a continuar o mapa, shot_number - numero do disparo a continuar (para casos de erros em mapas)

        shot_prog=0
        if self.parameters['make_clean_shot']==True:
            total=(self.parameters['n_shots']+1)*self.parameters['n_lin']*self.parameters['n_col']
        else:
            total=(self.parameters['n_shots'])*self.parameters['n_lin']*self.parameters['n_col']


        self.start_stages()

        messagebox.showwarning(title='Warning', message='Please align the sample!')

        self.start_laser()
        
        laser_not_ready, cooler_temp = self.laser_system.getting_ready()
        
        while laser_not_ready:
            laser_not_ready, cooler_temp = self.laser_system.getting_ready()
            #progressbar here

        coord=self.generate_coordinate(self.parameters['n_lin'], self.parameters['n_col'], self.parameters['step'])
        
        shot_number=0
        
        index_cur_coord=0
        T1 = []
        T2 = []
        T3 = []
        
        if resume:
            previous_shots = os.listdir(folder)
            if os.listdir(folder + "\\" + previous_shots[-1]) == []:
                index_cur_coord = len(previous_shots)-1
            else:
                index_cur_coord = len(previous_shots)
            cur_coord=resume
            #index_cur_coord=coord.index(cur_coord)
            
            

        for j in range(index_cur_coord, len(coord)):
            new_folder = folder + '\\' +'spot'+str(j+1)
            
            if os.path.exists(new_folder):
                shutil.rmtree(new_folder)
            os.mkdir(new_folder)

            x_pos= self.current_position[0]+coord[j][0]
            y_pos= self.current_position[1]+coord[j][1]
            
            #descomentei 2 linhas
            self.set_pos(x_pos, y_pos)
            QThread.msleep(250) #500
            #QThread.msleep(50)
            
            
            if self.parameters['make_clean_shot'] and shot_number==0:
            #if self.parameters['make_clean_shot']:

                print("Clean shot. Ready?")
                
                spectrometer_error=True
                spectrometer_error_count=0
                
                while spectrometer_error:
                    try:
                        self.start_spectrometer( integration_time=integration_time, delay_time = spec_delay_time)
                        spectrometer_error=False
                        
                    except RuntimeError:
                        spectrometer_error_count+=1
                        QThread.msleep(100)
                        
                       
                        if spectrometer_error_count%10==0:
                            print('erro no espertrometro (nº =)'+str(spectrometer_error_count))
                        
                        #INDEX RUN TIME ERRO - ver o que fazer
                        
                self.clean_shot(new_folder)

                shot_prog+=1
                #meas_progressBar.setValue((shot_prog/total)*100)
                QThread.msleep(500)
                
                
            if shot_number==0:     #para casos em que não queremos clean shot e queremos continuar um mapa que esta a meioF
                shot_number=1


            for i in range(shot_number-1, self.parameters['n_shots']):
                spectrometer_error=True
                spectrometer_error_count=0
                shot_number=i+1
                
                while spectrometer_error:
                    try:
                        self.start_spectrometer( integration_time=integration_time, delay_time = spec_delay_time)
                        spectrometer_error=False
                        
                    except RuntimeError:
                        spectrometer_error_count+=1
                        QThread.msleep(100)
                        
                       
                        if spectrometer_error_count%10==0:
                            print('erro no espertrometro (nº =)'+str(spectrometer_error_count))
                        
                        #INDEX RUN TIME ERRO - ver o que fazer
                        

                #Descomentei 1 linha
                QThread.msleep(250)  #500
                #QThread.msleep(50)
                
                print("Single shot...",end='\t')
                
                t0 = time.time()
               
                self.laser_system.laser.single_shot()
                shot_prog+=1
                #meas_progressBar.setValue((shot_prog/total)*100)
               
                #QThread.msleep(500)
                #QThread.msleep(10)
                
                self.set_pos(x_pos, y_pos)
                
                t1 = time.time()
                
                x, y = self.spec_system.plot_data()
                
                """
                if peak!=None:
                    x_comp=np.ndarray.flatten(np.array(x))
                    y_comp=np.ndarray.flatten(np.array(y))
                    #x_comp=[np.concatenate(x_comp, i for i in x)]
                    index = (np.abs(x_comp - float(peak))).argmin()
            
                    x_peak=[x_comp[i] for i in range(max(index-10, 0), min(index+10, x_comp.size))]
                    y_peak=[y_comp[j] for j in range(max(index-10, 0), min(index+10, y_comp.size))]
                    graphic.update_figure(x, y, x_peak, y_peak, element)
        
                else:
                    graphic.update_figure(x, y)
                """
                
                print("done.")
                
                t2 = time.time()
                
                
                #QThread.msleep(500)
                QThread.msleep(10)
                self.spec_system.save_data_map(x_pos=x_pos,y_pos=y_pos,folder=new_folder, shot_number=i+1)
                
                t3 =time.time()
                T1.append(str(t1-t0) + " s")
                T2.append(str(t2-t0) + " s")
                T3.append(str(t3-t0) + " s")
            
            shot_number=0
            
   
                               
        self.save_experiment_parameters(folder, 'map')
        self.hibernate()
    
    

    def pellets(self, folder, resume=False):
        
        os.mkdir(folder)
        
        repetitions=10
          
        delays=[370, 340, 370, 340, 370, 340]
        n_delays=len(delays)

        shot_prog=0
        if self.parameters['make_clean_shot']==True:
            total=(self.parameters['n_shots']+1)*repetitions*n_delays
        else:
            total=(self.parameters['n_shots'])*repetitions*n_delays

        delays_total=[]
        for delay in delays:
            delays_total+=[delay]*repetitions
        print(len(delays_total))
            

        self.start_stages()

        messagebox.showwarning(title='Warning', message='Please align the sample!')

        self.start_laser()
        
        coord=self.generate_coordinate_pellets(step=self.parameters['step'], rep=repetitions, len_QS=n_delays)
        
        laser_not_ready, cooler_temp = self.laser_system.getting_ready()
        print(cooler_temp)
        
        while laser_not_ready:
            print(cooler_temp)
            laser_not_ready, cooler_temp = self.laser_system.getting_ready()
            #progressbar here
            
        index_cur_coord=0
        
        if resume:
            cur_coord=resume
            index_cur_coord=coord.index(cur_coord)
            
        for j in range(index_cur_coord, len(coord)-1):
        #for j, delay in enumerate(delays_total):
            
            delay=delays_total[j]
            
            new_folder = folder + '\\' +str(delay)+'spot'+str(j+1)
            
            if os.path.exists(new_folder):
                shutil.rmtree(new_folder)
            os.mkdir(new_folder)
            
            x_pos = self.current_position[0]+coord[j][0]
            y_pos = self.current_position[1]+coord[j][1]

            print(x_pos, y_pos)
            self.set_pos(x_pos, y_pos)
            
                
            if self.parameters['make_clean_shot']:
                print("Clean shot. Ready?")
                self.start_spectrometer()
                self.clean_shot(new_folder)
                shot_prog+=1
                #meas_progressBar.setValue((shot_prog/total)*10)
                
                QThread.msleep(500)

            
            for i in range(0, self.parameters['n_shots']):

                self.start_spectrometer()
                print(delay)
                
                new_parameters={'delay':delay}
                self.laser_system.set_parameters(new_parameters)
                
                QThread.msleep(200)
                print("Single shot...",end='\t')
                self.laser_system.single_shot()
                shot_prog+=1
                #meas_progressBar.setValue((shot_prog/total)*10)

                QThread.msleep(200)

                x, y = self.spec_system.plot_data()
                
                '''
                if peak!=None:
                    x_comp=np.ndarray.flatten(np.array(x))
                    y_comp=np.ndarray.flatten(np.array(y))
                    #x_comp=[np.concatenate(x_comp, i for i in x)]
                    index = (np.abs(x_comp - float(peak))).argmin()
            
                    x_peak=[x_comp[i] for i in range(max(index-10, 0), min(index+10, x_comp.size))]
                    y_peak=[y_comp[j] for j in range(max(index-10, 0), min(index+10, y_comp.size))]
                    graphic.update_figure(x, y, x_peak, y_peak, element)
        
                else:
                    graphic.update_figure(x, y)  
                '''
                
                print("done.")

                self.spec_system.save_data_map(x_pos=x_pos,y_pos=y_pos, folder=new_folder, shot_number=i+1)
                

        self.hibernate()
        
        
        
        
        
    def multi_energy(self, folder, resume=False):
        
        os.mkdir(folder)
        
        repetitions=5
          
        delays=[390, 360, 340, 320, 300]
        n_delays=len(delays)

        shot_prog=0
        if self.parameters['make_clean_shot']==True:
            total=(self.parameters['n_shots']+1)*repetitions*n_delays
        else:
            total=(self.parameters['n_shots'])*repetitions*n_delays

        delays_total=[]
        for delay in delays:
            delays_total+=[delay]*repetitions
        print(delays_total)
            

        self.start_stages()

        messagebox.showwarning(title='Warning', message='Please align the sample!')

        self.start_laser()
        
        coord=self.generate_coordinate_pellets(step=self.parameters['step'], rep=repetitions, len_QS=n_delays)
        
        laser_not_ready, cooler_temp = self.laser_system.getting_ready()
        print(cooler_temp)
        
        while laser_not_ready:
            print(cooler_temp)
            laser_not_ready, cooler_temp = self.laser_system.getting_ready()
            #progressbar here
            
        index_cur_coord=0
        
        if resume:
            cur_coord=resume
            index_cur_coord=coord.index(cur_coord)
        
        print(len(coord))
        for j in range(index_cur_coord, len(coord)-1):
        #for j, delay in enumerate(delays_total):
            
            delay=delays_total[j]
            
            new_folder = folder + '\\' +str(delay)+'spot'+str(j+1)
            
            if os.path.exists(new_folder):
                shutil.rmtree(new_folder)
            os.mkdir(new_folder)
            
            x_pos = self.current_position[0]+coord[j][0]
            y_pos = self.current_position[1]+coord[j][1]

            print(x_pos, y_pos)
            self.set_pos(x_pos, y_pos)
            
                
            if self.parameters['make_clean_shot']:
                print("Clean shot. Ready?")
                self.start_spectrometer()
                self.clean_shot(new_folder)
                shot_prog+=1
                #meas_progressBar.setValue((shot_prog/total)*10)
                
                QThread.msleep(500)

            
            for i in range(0, self.parameters['n_shots']):

                self.start_spectrometer()
                print(delay)
                
                new_parameters={'delay':delay}
                self.laser_system.set_parameters(new_parameters)
                
                QThread.msleep(200)
                print("Single shot...",end='\t')
                self.laser_system.single_shot()
                shot_prog+=1
                #meas_progressBar.setValue((shot_prog/total)*10)

                QThread.msleep(200)

                x, y = self.spec_system.plot_data()
                
                '''
                if peak!=None:
                    x_comp=np.ndarray.flatten(np.array(x))
                    y_comp=np.ndarray.flatten(np.array(y))
                    #x_comp=[np.concatenate(x_comp, i for i in x)]
                    index = (np.abs(x_comp - float(peak))).argmin()
            
                    x_peak=[x_comp[i] for i in range(max(index-10, 0), min(index+10, x_comp.size))]
                    y_peak=[y_comp[j] for j in range(max(index-10, 0), min(index+10, y_comp.size))]
                    graphic.update_figure(x, y, x_peak, y_peak, element)
        
                else:
                    graphic.update_figure(x, y)  
                '''
                
                print("done.")

                self.spec_system.save_data_map(x_pos=x_pos,y_pos=y_pos, folder=new_folder, shot_number=i+1)
                

        self.hibernate()
                
          
        
    def clean_shot(self, folder):
        previous_delay=self.laser_system.laser.delay
        
        parameters_to_change = {'delay':self.laser_system.laser.cdelay}
        print(parameters_to_change)
        self.laser_system.set_parameters(parameters_to_change)
        
        print("Cleaning shot...",end='\t')
        print()
        #QThread.msleep(200)
        self.laser_system.single_shot()
        QThread.msleep(200)
      

        x, y = self.spec_system.plot_data()
        
        #self.GUI_plot(graphic,peak, x, y)


        self.spec_system.save_data_clean_shot(folder=folder)
        print("done.")
        parameters_to_change = {'delay':previous_delay}
        self.laser_system.set_parameters(parameters_to_change)







   
        
        
        
        
   
        
    
    
      

                
               
               

                
        

