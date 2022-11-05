import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QWidget, QPushButton, QApplication, QVBoxLayout
 
from tkinter import *
from tkinter import filedialog
from multiprocessing import Process, Manager, Lock
import os

from Core.Experiment import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')

from numpy import arange, sin, pi





class MyMplCanvas(FigureCanvas):
    
    def __init__(self, parent=None, width=10, height=6, dpi=200):
        fig = Figure(figsize=(width, height), dpi=dpi)
        gs = fig.add_gridspec(3, 4, left=0.07, right=0.97, wspace=0.4)
        #self.axes = fig.add_subplot(111)
        self.ax1 = fig.add_subplot(gs[0:, :3])
        self.ax2 = fig.add_subplot(gs[0:, -1])
        self.ax1.set_title('Complete Spectrum', fontsize=9)
        self.ax2.set_title('Selected Peak', fontsize=9)
        
        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass




class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
       

    def compute_initial_figure(self):
        self.ax1.set_xlim(150, 950)
        self.ax1.set_xlabel(r'$\lambda$ (nm)')
        self.ax1.set_ylabel('Intensity (counts)')
        self.ax2.set_xlabel(r'$\lambda$ (nm)')
        self.ax2.set_ylabel('Intensity (counts)')


    def update_figure(self, x, y, x_peak=[], y_peak=[], element=''):
        
        self.ax1.cla()
        self.ax2.cla()

        self.ax1.set_title('Complete Spectrum', fontsize=9)
        self.ax2.set_title('Selected Peak ('+str(element) + ')', fontsize=9)
        self.ax1.set_xlim(150, 950)
        self.ax1.set_xlabel(r'$\lambda$ (nm)')
        self.ax1.set_ylabel('Intensity (counts)')
        self.ax2.set_xlabel(r'$\lambda$ (nm)')
        self.ax2.set_ylabel('Intensity (counts)')
        #self.ax1.set_ylim(0, max(y)+max(y)/100)
        #self.ax2.set_ylim(0, max(y_peak)+max(y_peak)/100)
        for spec in range(0, len(x)):
            self.ax1.plot (x[spec], y[spec])
            
        self.ax2.plot (x_peak, y_peak, 'b')
        
        self.draw()

        
        
class MainWindow(QtWidgets.QMainWindow):
 
        def __init__(self):
                super().__init__()
                self.setGeometry(300, 225, 500, 150)
                self.w = None  # No external window yet.
                
                self.label1 = QtWidgets.QLabel(self)
                self.label1.setGeometry(QtCore.QRect(30, 0, 150, 100))
                self.label1.setObjectName("label")
                self.label1.setText('Select your LIBS system:')
                self.label1.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
                
                self.NDYAG =  QtWidgets.QPushButton(self)
                self.NDYAG.setGeometry(QtCore.QRect(30, 75, 120, 45))
                self.NDYAG.setText("Nd:YAG System")
                self.NDYAG.setObjectName("pushButton_4")
                self.NDYAG.clicked.connect(self.show_new_window)
                self.NDYAG.setStyleSheet("font: 9pt \"MS Shell Dlg 2\";")
                
                self.Fiber_laser =  QtWidgets.QPushButton(self)
                self.Fiber_laser.setGeometry(QtCore.QRect(185, 75, 120, 45))
                self.Fiber_laser.setText("Fiber System")
                self.Fiber_laser.setObjectName("pushButton_4")
                self.Fiber_laser.clicked.connect(self.show_new_window)
                self.Fiber_laser.setStyleSheet("font: 9pt \"MS Shell Dlg 2\";")
                
                self.simulator =  QtWidgets.QPushButton(self)
                self.simulator.setGeometry(QtCore.QRect(345, 75, 120, 45))
                self.simulator.setText("Simulator")
                self.simulator.setObjectName("pushButton_4")
                self.simulator.clicked.connect(self.show_new_window)
                self.simulator.setStyleSheet("font: 9pt \"MS Shell Dlg 2\";")
               
               
                     
          
                
                #self.setCentralWidget(self.button)
                
        def show_new_window(self, checked):
                if self.w is None:
                        self.w = Window()
                self.w.show()
                self.close()
                


           
class Window(QWidget):

        def __init__(self):
                super(Window, self).__init__()
                self.setGeometry(50, 50, 1430, 902)
                self.setWindowTitle("LIBS")
                self.setupUi()        

        def setupUi(self):

                self.label = QtWidgets.QLabel(self)
                self.label.setGeometry(QtCore.QRect(20, 50, 47, 13))
                self.label.setObjectName("label")
                self.label_2 = QtWidgets.QLabel(self)
                self.label_2.setGeometry(QtCore.QRect(20, 80, 91, 16))
                self.label_2.setObjectName("label_2")
                self.browse_b = QtWidgets.QPushButton(self)
                self.browse_b.setGeometry(QtCore.QRect(1330, 50, 81, 23))
                self.browse_b.setObjectName("pushButton")
                self.sample_n = QtWidgets.QLineEdit(self)
                self.sample_n.setGeometry(QtCore.QRect(90, 80, 1221, 20))
                self.sample_n.setObjectName("lineEdit")
                self.path_dir = QtWidgets.QLineEdit(self)
                self.path_dir.setGeometry(QtCore.QRect(90, 50, 1221, 20))
                self.path_dir.setObjectName("lineEdit_2")
                self.label_3 = QtWidgets.QLabel(self)
                self.label_3.setGeometry(QtCore.QRect(10, 120, 161, 41))
                self.label_3.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
                self.label_3.setObjectName("label_3")
                self.label_4 = QtWidgets.QLabel(self)
                self.label_4.setGeometry(QtCore.QRect(10, 0, 141, 41))
                self.label_4.setMinimumSize(QtCore.QSize(141, 0))
                self.label_4.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
                self.label_4.setObjectName("label_4")
                self.label_5 = QtWidgets.QLabel(self)
                self.label_5.setGeometry(QtCore.QRect(30, 180, 47, 13))
                self.label_5.setText("")
                self.label_5.setObjectName("label_5")
                self.frame1 = QtWidgets.QFrame(self)
                self.frame1.setGeometry(QtCore.QRect(20, 250, 371, 151))
                self.frame1.setStyleSheet("background-color: rgb(230, 230, 230);")
                self.frame1.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame1.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame1.setObjectName("frame1")
                self.label_6 = QtWidgets.QLabel(self.frame1)
                self.label_6.setGeometry(QtCore.QRect(10, 10, 111, 16))
                self.label_6.setStyleSheet("font: 9pt \"MS Shell Dlg 2\";")
                self.label_6.setObjectName("label_6")
                self.label_11 = QtWidgets.QLabel(self.frame1)
                self.label_11.setGeometry(QtCore.QRect(10, 40, 81, 16))
                self.label_11.setObjectName("label_11")
                self.no_b = QtWidgets.QRadioButton(self.frame1)
                self.no_b.setGeometry(QtCore.QRect(100, 40, 31, 17))
                self.no_b.setObjectName("checkBox_4")
                self.yes_b = QtWidgets.QRadioButton(self.frame1)
                self.yes_b.setGeometry(QtCore.QRect(100, 60, 41, 17))
                self.yes_b.setObjectName("checkBox_5")
                self.label_12 = QtWidgets.QLabel(self.frame1)
                self.label_12.setGeometry(QtCore.QRect(160, 60, 141, 20))
                self.label_12.setObjectName("label_12")
                self.c_delay_box = QtWidgets.QLineEdit(self.frame1)
                self.c_delay_box.setGeometry(QtCore.QRect(300, 60, 41, 20))
                self.c_delay_box.setObjectName("lineEdit_3")
                self.label_13 = QtWidgets.QLabel(self.frame1)
                self.label_13.setGeometry(QtCore.QRect(350, 60, 31, 16))
                self.label_13.setObjectName("label_13")
                self.label_14 = QtWidgets.QLabel(self.frame1)
                self.label_14.setGeometry(QtCore.QRect(10, 90, 181, 16))
                self.label_14.setObjectName("label_14")
                self.n_shots_box = QtWidgets.QLineEdit(self.frame1)
                self.n_shots_box.setGeometry(QtCore.QRect(300, 90, 41, 20))
                self.n_shots_box.setObjectName("lineEdit_4")
                self.label_15 = QtWidgets.QLabel(self.frame1)
                self.label_15.setGeometry(QtCore.QRect(10, 120, 121, 16))
                self.label_15.setObjectName("label_15")
                self.q_switch_box= QtWidgets.QLineEdit(self.frame1)
                self.q_switch_box.setGeometry(QtCore.QRect(300, 120, 41, 20))
                self.q_switch_box.setObjectName("lineEdit_5")
                self.label_16 = QtWidgets.QLabel(self.frame1)
                self.label_16.setGeometry(QtCore.QRect(350, 120, 16, 16))
                self.label_16.setObjectName("label_16")
                self.frame1_2 = QtWidgets.QFrame(self)
                self.frame1_2.setGeometry(QtCore.QRect(20, 520, 371, 131))
                self.frame1_2.setStyleSheet("background-color: rgb(230, 230, 230);")
                self.frame1_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame1_2.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame1_2.setObjectName("frame1_2")
                self.label_7 = QtWidgets.QLabel(self.frame1_2)
                self.label_7.setGeometry(QtCore.QRect(10, 10, 111, 16))
                self.label_7.setStyleSheet("font: 9pt \"MS Shell Dlg 2\";")
                self.label_7.setObjectName("label_7")
                self.label_21 = QtWidgets.QLabel(self.frame1_2)
                self.label_21.setGeometry(QtCore.QRect(10, 40, 121, 20))
                self.label_21.setObjectName("label_21")
                self.label_22 = QtWidgets.QLabel(self.frame1_2)
                self.label_22.setGeometry(QtCore.QRect(10, 70, 121, 20))
                self.label_22.setObjectName("label_22")
                self.label_23 = QtWidgets.QLabel(self.frame1_2)
                self.label_23.setGeometry(QtCore.QRect(10, 100, 121, 20))
                self.label_23.setObjectName("label_23")
                self.n_columns_box = QtWidgets.QLineEdit(self.frame1_2)
                self.n_columns_box.setGeometry(QtCore.QRect(300, 40, 41, 20))
                self.n_columns_box.setText("")
                self.n_columns_box.setObjectName("lineEdit_8")
                self.n_lines_box = QtWidgets.QLineEdit(self.frame1_2)
                self.n_lines_box.setGeometry(QtCore.QRect(300, 70, 41, 20))
                self.n_lines_box.setText("")
                self.n_lines_box.setObjectName("lineEdit_9")
                self.step_box = QtWidgets.QLineEdit(self.frame1_2)
                self.step_box.setGeometry(QtCore.QRect(300, 100, 41, 20))
                self.step_box.setText("")
                self.step_box.setObjectName("lineEdit_10")
                self.label_24 = QtWidgets.QLabel(self.frame1_2)
                self.label_24.setGeometry(QtCore.QRect(350, 100, 16, 16))
                self.label_24.setObjectName("label_24")
                self.frame1_3 = QtWidgets.QFrame(self)
                self.frame1_3.setGeometry(QtCore.QRect(20, 160, 371, 61))
                self.frame1_3.setStyleSheet("background-color: rgb(230, 230, 230);")
                self.frame1_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame1_3.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame1_3.setObjectName("frame1_3")
                self.label_8 = QtWidgets.QLabel(self.frame1_3)
                self.label_8.setGeometry(QtCore.QRect(10, 10, 111, 16))
                self.label_8.setStyleSheet("font: 9pt \"MS Shell Dlg 2\";")
                self.label_8.setObjectName("label_8")
                self.single_shot_b = QtWidgets.QRadioButton(self.frame1_3)
                self.single_shot_b.setGeometry(QtCore.QRect(10, 40, 101, 17))
                self.single_shot_b.setObjectName("checkBox")
                self.multi_shot_b = QtWidgets.QRadioButton(self.frame1_3)
                self.multi_shot_b.setGeometry(QtCore.QRect(150, 40, 70, 17))
                self.multi_shot_b.setObjectName("checkBox_2")
                self.pellets_b = QtWidgets.QRadioButton(self.frame1_3)
                self.pellets_b.setGeometry(QtCore.QRect(310, 40, 70, 17))
                self.pellets_b.setObjectName("checkBox_3")              
                self.frame1_4 = QtWidgets.QFrame(self)
                self.frame1_4.setGeometry(QtCore.QRect(20, 410, 371, 101))
                self.frame1_4.setStyleSheet("background-color: rgb(230, 230, 230);")
                self.frame1_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame1_4.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame1_4.setObjectName("frame1_4")
                self.label_10 = QtWidgets.QLabel(self.frame1_4)
                self.label_10.setGeometry(QtCore.QRect(10, 10, 141, 16))
                self.label_10.setStyleSheet("font: 9pt \"MS Shell Dlg 2\";")
                self.label_10.setObjectName("label_10")
                self.label_17 = QtWidgets.QLabel(self.frame1_4)
                self.label_17.setGeometry(QtCore.QRect(10, 40, 121, 20))
                self.label_17.setObjectName("label_17")
                self.gate_time_box = QtWidgets.QLineEdit(self.frame1_4)
                self.gate_time_box .setGeometry(QtCore.QRect(300, 30, 41, 20))
                self.gate_time_box .setObjectName("lineEdit_6")
                self.label_18 = QtWidgets.QLabel(self.frame1_4)
                self.label_18.setGeometry(QtCore.QRect(350, 30, 16, 16))
                self.label_18.setObjectName("label_18")
                self.label_19 = QtWidgets.QLabel(self.frame1_4)
                self.label_19.setGeometry(QtCore.QRect(10, 70, 121, 20))
                self.label_19.setObjectName("label_19")
                self.integration_time_box = QtWidgets.QLineEdit(self.frame1_4)
                self.integration_time_box.setGeometry(QtCore.QRect(300, 70, 41, 20))
                self.integration_time_box.setObjectName("lineEdit_7")
                self.label_20 = QtWidgets.QLabel(self.frame1_4)
                self.label_20.setGeometry(QtCore.QRect(350, 70, 16, 16))
                self.label_20.setObjectName("label_20")
                self.start_b = QtWidgets.QPushButton(self)
                self.start_b.setGeometry(QtCore.QRect(40, 860, 75, 23))
                self.start_b.setObjectName("pushButton_3")
                self.pause_b = QtWidgets.QPushButton(self)
                self.pause_b.setGeometry(QtCore.QRect(160, 860, 75, 23))
                self.pause_b.setObjectName("pushButton_4")
                self.stop_b = QtWidgets.QPushButton(self)
                self.stop_b.setGeometry(QtCore.QRect(280, 860, 75, 23))
                self.stop_b.setObjectName("pushButton_5")
                self.heating_progressBar = QtWidgets.QProgressBar(self)
                self.heating_progressBar.setGeometry(QtCore.QRect(1060, 860, 101, 20))
                self.heating_progressBar.setProperty("value", 0)
                self.heating_progressBar.setObjectName("progressBar")
                self.heating_progressBar.setMaximum(326)
                self.heating_progressBar.setMinimum(300)
                self.measurement_progressBar = QtWidgets.QProgressBar(self)
                self.measurement_progressBar.setGeometry(QtCore.QRect(1300, 860, 101, 20))
                self.measurement_progressBar.setProperty("value", 0)
                self.measurement_progressBar.setObjectName("progressBar_2")
                self.label_25 = QtWidgets.QLabel(self)
                self.label_25.setGeometry(QtCore.QRect(990, 860, 71, 16))
                self.label_25.setObjectName("label_25")
                self.label_26 = QtWidgets.QLabel(self)
                self.label_26.setGeometry(QtCore.QRect(1200, 860, 101, 20))
                self.label_26.setObjectName("label_26")
                self.label_27 = QtWidgets.QLabel(self)
                self.label_27.setGeometry(QtCore.QRect(400, 130, 81, 16))
                self.label_27.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
                self.label_27.setObjectName("label_27")
                
                self.label_9 = QtWidgets.QLabel(self)
                self.label_9.setGeometry(QtCore.QRect(10, 660, 161, 41))
                self.label_9.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
                self.frame = QtWidgets.QFrame(self)
                self.frame.setGeometry(QtCore.QRect(20, 700, 371, 131))
                self.frame.setStyleSheet("background-color: rgb(230, 230, 230);")
                self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame.setObjectName("frame")
                self.label_34 = QtWidgets.QLabel(self.frame)
                self.label_34.setGeometry(QtCore.QRect(10, 70, 121, 20))
                self.label_34.setObjectName("label_34")
                self.element = QtWidgets.QLineEdit(self.frame)
                self.element.setGeometry(QtCore.QRect(300, 70, 41, 20))
                self.element.setText("")
                self.element.setObjectName("lineEdit_14")
                self.label_35 = QtWidgets.QLabel(self.frame)
                self.label_35.setGeometry(QtCore.QRect(10, 100, 121, 20))
                self.label_35.setObjectName("label_35")
                self.wave_value = QtWidgets.QLineEdit(self.frame)
                self.wave_value.setGeometry(QtCore.QRect(300, 100, 41, 20))
                self.wave_value.setText("")
                self.wave_value.setObjectName("lineEdit_15")
                self.label_36 = QtWidgets.QLabel(self.frame)
                self.label_36.setGeometry(QtCore.QRect(350, 100, 16, 16))
                self.label_36.setObjectName("label_36")
                self.label_37 = QtWidgets.QLabel(self.frame)
                self.label_37.setGeometry(QtCore.QRect(10, 10, 121, 20))
                self.label_37.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
                self.label_37.setObjectName("label_37")
                self.none_box = QtWidgets.QCheckBox(self.frame)
                self.none_box.setGeometry(QtCore.QRect(10, 40, 101, 17))
                self.none_box.setObjectName("checkBox_8")
                self.peak_box = QtWidgets.QCheckBox(self.frame)
                self.peak_box.setGeometry(QtCore.QRect(140, 40, 101, 17))
                self.peak_box.setObjectName("checkBox_7")
                self.map_box = QtWidgets.QCheckBox(self.frame)
                self.map_box.setGeometry(QtCore.QRect(300, 40, 101, 17))
                self.map_box.setObjectName("checkBox_6")
               
                self.frameN = QtWidgets.QFrame(self)
                self.frameN.setGeometry(QtCore.QRect(410, 160, 1001, 681))
                self.main_widget = QtWidgets.QWidget(self.frameN)
                l = QtWidgets.QVBoxLayout(self.frameN)
                self.dc = MyDynamicMplCanvas(self.frameN, width=1, height=1, dpi=100)
                l.addWidget(self.dc)
                self.frameN.setFocus()
                        
        
        #set text to labels
                self.label.setText("Directory")
                self.label_2.setText("Folder Name")
                self.browse_b.setText("Browse")
                self.label_3.setText("LIBS Measurement Settings")
                self.label_4.setText("Save Data Properties")
                self.label_6.setText("Laser Parameters")
                self.label_11.setText("Cleanning Shot:")
                self.yes_b.setText("Yes")
                self.no_b.setText("No")
                self.label_12.setText("If said Yes select Q-S.Delay:")
                self.c_delay_box.setText("410")
                self.label_13.setText(u"\u03bcs")
                self.label_14.setText("Nº of Shots per Spot (excluding c.s.):")
                self.n_shots_box.setText("1")
                self.label_15.setText("Shots Q-Switch Delay:")
                self.q_switch_box.setText("")
                self.label_16.setText(u"\u03bcs")
                self.label_7.setText("Stages Parameters")
                self.label_21.setText("Nº of columns (x): ")
                self.label_22.setText("Nº of lines (y): ")
                self.label_23.setText("Step:")
                self.label_24.setText("mm")
                self.label_8.setText("Mesurement Type")
                self.single_shot_b.setText("Single Shot")
                self.multi_shot_b.setText("Multi Shot")
                self.pellets_b.setText("Pellets")
                self.label_10.setText("Spectrometer Parameters")
                self.label_17.setText("Gate Delay Time:")
                self.gate_time_box .setText("0")
                self.label_18.setText(u"\u03bcs")
                self.label_19.setText("Integration Time:")
                self.integration_time_box.setText("1.05")
                self.label_20.setText("ms")
                self.start_b.setText("Start")
                self.pause_b.setText("Pause")
                self.stop_b.setText("Stop")
                self.label_25.setText("Laser Heating ")
                self.label_26.setText("LIBS measurements")
                self.label_27.setText("LIBS Spectrum")
                self.label_9.setText("LIBS Data Analysis")
                self.label_34.setText("Element:")
                self.label_35.setText("Line:")
                self.label_36.setText("nm")
                self.label_37.setText("Analysis Type")
                self.none_box.setText("None")
                self.peak_box.setText("Peak Intensity")
                self.map_box.setText("Mapping")
                

                self.button_functions()
                self.show()

        def button_functions(self):
                
                
                self.browse_b.clicked.connect(self.browse)
                
                

                if self.start_b.text()=='Start':
                        self.start_b.clicked.connect(self.start)
                if self.start_b.text()=='Continue':
                        self.start_b.clicked.connect(self.continue_f)
                        
                self.pause_b.clicked.connect(self.pause)
                self.stop_b.clicked.connect(self.stop)

                
        
        def browse(self):
                root = Tk()
                root.withdraw()
                root.attributes('-topmost',True)                                                                       

                folder_p = filedialog.askdirectory(parent=root, title='ESCOLHER PASTA COM OS DADOS EXPERIMENTAIS') 
                
                self.path_dir.setText(folder_p)
                
                
        def create_folder(self):
                folder_path= r'%s'%self.path_dir.text()
                self.folder=os.path.join(folder_path, self.sample_n.text())
                print(self.folder)
                try:
                        os.mkdir(self.folder)
                except:
                        None


        def start(self):
                self.create_folder()
                print('Folder é esta'+str(self.folder))
                self.parameters={}
                self.parameters['make_clean_shot']=False
                self.parameters['cdelay']=np.nan
                if self.yes_b.isChecked():
                        print('clean_shot_selected')
                        self.parameters['make_clean_shot']=True
                        self.parameters['cdelay']=int(self.c_delay_box.text())
                self.parameters['n_shots']=int(self.n_shots_box.text())
                self.element_name=None
                self.peak_value=None
                

                keys_values={'n_lin':self.n_lines_box.text, 'n_col':self.n_columns_box.text, 'step':self.step_box.text, 'delay':self.q_switch_box.text}
                values=[]
                for key_name, values in keys_values.items():
                        try:
                                if key_name=='step':
                                        self.parameters[key_name]=float(values())
                                else:
                                        self.parameters[key_name]=int(values())
                        except:
                                self.parameters[key_name]=0

                                if key_name=='delay':
                                        self.parameters[key_name]=410

                        
                #self.parameters['gate_time']=int(self.gate_time_box.text())                        Falta adicionar uma função para isto
                #self.parameters['integration_time']=int(self.integration_time_box.tex())           Falta adicionar uma função para isto

                
                print(self.parameters)
                if self.path_dir.text()=='':
                        QMessageBox.about(self, "Warning", "Any path selected to save data!")



                else:
            
                        if self.single_shot_b.isChecked():
                                print('Single Shot Selected')
                               
                                if self.peak_box.isChecked():
                                        self.peak_value=self.wave_value.text()
                                        self.element_name=self.element.text()

                                if self.map_box.isChecked():
                                        QMessageBox.about(self, "Warning", "Inappropriate mapping analysis selection")
                                Experiment1=Experiment(system="NdYAG", parameters=self.parameters)
                                #Experiment1.set_system_parameters(system="NdYAG", parameters=self.parameters)
                                #Experiment1.set_system_parameters(parameters=self.parameters)
                                print(Experiment1.parameters)
                                
                                if __name__ == '__main__':
                                    mgr = Manager()
                                    cooler_temperature = mgr.list([])
                                    shot_progress = mgr.list([])
                                    x_shared = mgr.list([])
                                    y_shared = mgr.list([])
                                    lock = Lock()
                                
                                    experiment_process=Process(target=Experiment1.single_shot, args = (self.folder,cooler_temperature,shot_progress,x_shared,y_shared,lock))#self.heating_progressBar
                                    experiment_process.start()
                                else:
                                    print('not main')
                                end_bool = True
                                while end_bool:
                                    lock.acquire()
                                    print(cooler_temperature)
                                    print(x_shared)
                                    print(y_shared)
                                    lock.release
                                    time.sleep(1)
                                     
                               
                                print('ACABOU')
                                
                                
                        elif self.multi_shot_b.isChecked():
                                print('Multi Shot Selected')

                                if self.peak_box.isChecked():
                                        self.peak_value=self.wave_value.text()
                                        self.element_name=self.element.text()

                                if self.map_box.isChecked():
                                        QMessageBox.about(self, "Warning", "Inappropriate mapping analysis selection")
                                Experiment.set_system_parameters(parameters=self.parameters)
                                Experiment.multi_shot(folder=self.folder, parameters=self.parameters, graphic=self.dc, element=self.element_name, peak=self.peak_value, progressBar=self.heating_progressBar, meas_progressBar=self.measurement_progressBar)
                        
                        elif self.pellets_b.isChecked():
                                print('Pellets Selected')
                                if self.peak_box.isChecked():
                                        self.peak_value=self.wave_value.text()
                                        self.element_name=self.element.text()

                                if self.map_box.isChecked():
                                        QMessageBox.about(self, "Warning", "Inappropriate mapping analysis selection")

                                self.experiment.set_system_parameters(system="NdYAG", parameters=self.parameters)
                                self.experiment.pellets(folder=self.folder, parameters=self.parameters, graphic=self.dc, element=self.element_name, peak=self.peak_value, progressBar=self.heating_progressBar, meas_progressBar=self.measurement_progressBar)
                                
                        
                        else:
                                QMessageBox.about(self, "Warning", "Any measurement type selected!")


        def pause(self):
                
                Experiment.pause_system()
                self.start_b.setText("Continue")
                self.start_b.clicked.connect(self.continue_f)
                print('Pause')


        def continue_f(self):
                continue_thread=threading.Thread(target=Experiment.start_laser, args=(self.heating_progressBar,))
                continue_thread.start()
                print('Continuing')


        def stop(self):
                
                print('Stop1')
               
                Experiment.hibernate()
                print('Stop2')
                
                self.start_b.setText('Start')
                self.start_b.clicked.connect(self.start)
                print('Stop3')


                

def run():
        app=QtWidgets.QApplication(sys.argv)
        w = MainWindow()
        w.show()
        app.exec()
        
        #GUI=Window()
        #sys.exit(app.exec())


run()



    
    
    




