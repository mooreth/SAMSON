import importlib
import os
import sys
import math
import shutil
import subprocess
import traceback #Used for logging
from datetime import datetime #used for naming autoback up files


# [DM] use the logging to log exceptions
import logging
# [DM] Configure the logging, can be done in other places, e.g. in __main__
logging.basicConfig(filename="C:\\Users\\Public\\gamess-64\\SAMSON_log.txt", level=logging.ERROR)

from ctypes import alignment
from turtle import right
from qtpy.QtCore import QFileInfo
from PyQt5.QtWidgets import QPushButton, QLabel, QDoubleSpinBox, QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout, QDialog, QFileDialog, QLineEdit
from PyQt5.QtCore import Qt

import samson as sam
from samson.Facade import SAMSON        # SAMSON Facade - main interface of SAMSON
from samson.DataModel import Quantity   # Quantities: length, mass, time, etc
from samson.DataModel import Type       # Types: position3, etc
from samson.DataModel.DataGraph import Node
from samson.Modeling.StructuralModel import Atom

class RunGAMESS(QDialog):

    def __init__(self, parent=None):
    
        super(RunGAMESS, self).__init__(parent)
        # [DM] it is better to initialize all the internal variables in the init
        self.input_filename = ''        
    
        # create widgets
            
        #Basis label and NGAUSS number
        self.basisLabel = QLabel("GBASIS = STO", self)
        
        NGAUSS_list = ["2","3","4","5","6"]
        self.NGAUSS = QComboBox(self)
        self.NGAUSS.addItems(NGAUSS_list)     
        
        #Calculation Type
        runtypeList = ["Single Point Energy", "Equilibrium Geometry" ]
        self.runtype = QComboBox(self)
        self.runtype.addItems(runtypeList)
        
        #Self-consistent field type selector. Only offering restricted and unrestricted Hartree fock for now
        SCFTYPList = ["RHF", "UHF" ]
        self.SCFTYP = QComboBox(self)
        self.SCFTYP.addItems(SCFTYPList)
        
        #Check this box if no symetry is used in the calculation
        self.usesymBox = QCheckBox("Symmetry is used in this calculation",self)
        self.usesymBox.setChecked(False)
        
        self.symmetryLabel = QLabel("GROUP", self)
        self.symmetryLine =  QLineEdit(self)
        self.symmetryLine.setEnabled(False)
        
        ##Checkbox to choose between using a seperate input file or GUI options
        self.useInputFile = QCheckBox("Use input file instead",self)
        self.useInputFile.setChecked(False)
        
        self.useInputLabel = QLabel("Use a input file", self)
    
        #load input file
        self.btnInput = QPushButton("Load input file")
        self.btnInput.setEnabled(False)
       
        #Comment line
        self.commentLabel = QLabel("Comment line:", self)
        self.commentLine =  QLineEdit(self)
        
        #run calculation
        self.button = QPushButton("Run Calculation", self)
         
        # set layout
        distanceLayout = QHBoxLayout()
        layout = QVBoxLayout()
        
        layout.addLayout(distanceLayout)
        
        layout.addWidget(self.usesymBox)
        layout.addWidget(self.SCFTYP)
        layout.addWidget(self.runtype)
        
        #use input file controls
        layout.addWidget(self.useInputFile)
        
        layout.addWidget(self.useInputLabel)
        layout.addWidget(self.btnInput)
        
        #run calc
        layout.addWidget(self.button)
       
        distanceLayout.addWidget(self.symmetryLabel)
        distanceLayout.addWidget(self.symmetryLine)        
        
        distanceLayout.addWidget(self.basisLabel)
        distanceLayout.addWidget(self.NGAUSS)
        
        distanceLayout.addWidget(self.commentLabel)
        distanceLayout.addWidget(self.commentLine)      
        
        self.setLayout(layout)
        self.setMinimumWidth(300)
        
        # connect signals to slot
        
        self.button.clicked.connect(self.runCalculation)
        self.btnInput.clicked.connect(self.getfile)  #I don't think I need this?
        
        self.usesymBox.stateChanged.connect(self.toggleGroupLine)
        
        #disable UI calculation widgets and enable load input file button
        self.useInputFile.stateChanged.connect(self.switchInputType)
      
    def output_check(self):
        now = datetime.now()
        current = now.strftime("%H_%M_%S")
        log = open("C:\\Users\\Public\\gamess-64\\SAMSON_log.txt", "a") 
        #check for input
        try:
            path = '/Users/Public/gamess-64/GAMESS_input.ini'
            check = os.path.isfile(path)
           
            if check == True:
                old_file = os.path.join("C:\\Users\\Public\\gamess-64\\", "GAMESS_input.ini")
                new_file = os.path.join("C:\\Users\\Public\\gamess-64\\", "GAMESS_input_" + current + ".ini")
                os.rename(old_file, new_file)
                log.write("Existing input file backed up" + "\n")
            
        except:
            logging.exception("An error occurred")
            pass           
        #check for output
        try:
            path = '/Users/Public/gamess-64/out.out'
            check = os.path.isfile(path)
            
            if check == True:
                old_file = os.path.join("C:\\Users\\Public\\gamess-64\\", "out.out")
                new_file = os.path.join("C:\\Users\\Public\\gamess-64\\", "out_" + current + ".out")
                os.rename(old_file, new_file)
                log.write("Existing output file backed up" + "\n")
            
        except:
            logging.exception("An error occurred")
            pass   
   
   
    def write_atoms(self, filepath_X, filename_X, origin):
        #origin flags is the calculation is being run from a already exisiting input file (=1) for from UI settings (2) BS Alters the filepath and filenames accourdingly
        #I'm sure this is a sloppy way to do this.
      
        if origin == 1:
            file = open(filename_X, 'r') #tryng name
            igot = file.readlines()
            log = open("C:\\Users\\Public\\gamess-64\\SAMSON_log.txt", "a")
            for count, line in enumerate(igot):
                try:
                    if line in ["$END"]:
                        insert_val = count-1
                    else:
                        insert_val = 6                        
                except:
                    
                    logging.exception("An error occurred")
        else:
            insert_val = 6
        
        insert_index_eng = insert_val ######if origin is one we should check what the insert_index needs to be ortherwise =6
        indexer = SAMSON.getNodes('n.t a')                # returns all atom nodes
        #print(indexer.size)                               # returns size of the indexer
                
        for atom in range(0, indexer.size):
            myAtom = indexer[atom]
            Atom_x =myAtom.getX().angstrom
            Atom_y =myAtom.getY().angstrom
            Atom_z =myAtom.getZ().angstrom
            
            Atom_type = myAtom.elementSymbol
            proton_number = int(myAtom.elementType)
            
            input_line = Atom_type + "      "+ str(proton_number) + "      " +  str(round(Atom_x,3)) + "      "+ str(round(Atom_y,3)) + "      "+ str(round(Atom_z,3)) + " !"  + "\n"

            if origin == 2:
                insert_index_eng = 6
            
                with open(filepath_X + filename_X, "r") as f: 
                                                                contents = f.readlines()
    
                                                                contents.insert(insert_index_eng, input_line)
    
                with open(filepath_X + filename_X, "w") as f:
                                                                contents = "".join(contents) 
                                                                f.write(contents)  
            
            else:
                with open(filepath_X, "r") as f: 
                                                                contents = f.readlines()
    
                                                                contents.insert(insert_index_eng, input_line)
    
                with open(filepath_X, "w") as f:
                                                                contents = "".join(contents) 
                                                                f.write(contents)                  
                

       
    def runCalculation(self):
        SAMSON.beginHolding("Calculate")
        
        #Let's first check if there is a GAMESS output file in the directory alreadt, and if there is we will rename it so it doesn't get over written
        self.output_check()
        
     
        try:        
        
            if self.useInputFile.isChecked():
                
                try:
                    # [DM] there might be an exception if such path doesn't exist
                    log = open("C:\\Users\\Public\\gamess-64\\SAMSON_log.txt", "a")
                except Exception as e: 
                    # [DM] Log the exception
                    logging.exception("An error occurred")
                    pass
                
                # [DM] Create a QFileInfo object for the file
                file_info = QFileInfo(self.input_filename)
                # Access various properties of the file
                
                filename_X_in = file_info.fileName()
                filename_X = filename_X_in.replace(" " , "_")
                os.rename(filename_X_in, filename_X) #subprocess doesn't handle file names with white spaces in them. After trying to fix this for a while I decided just to remove them for now. 
                #filename_X = file_info.fileName()
                filepath_X = file_info.filePath() 
                fileout_X = "out.out"
                origin = 1 
                self.write_atoms(filepath_X, filename_X, origin)
                os.chdir('C:\\Users\\Public\\gamess-64')
                subprocess.run('C:\\Users\\Public\\gamess-64\\rungms.bat ' + filename_X  + ' 2022.R2.intel 1 '+ fileout_X, shell=True)  

                try:
          
                    pass
        
                except Exception as e: 
                    # Log the exception
                    logging.exception("An error occurred")
                    pass
                
                self.importOptGeo() 
            
            else: #this uses settings from the UI
                try:
                    # [DM] there might be an exception if such path doesn't exist
                    log = open("C:\\Users\\Public\\gamess-64\\SAMSON_log.txt", "a")
                    
                except Exception as e: 
                    # [DM] Log the exception
                    logging.exception("An error occurred")
                    pass                
                
                origin = 2 
                
                filepath_X = 'C:\\Users\\Public\\gamess-64\\'
                filename_X = 'GAMESS_input.ini'
                fileout_X = 'out.out'                     
                
                with open(filepath_X + filename_X, "a") as f: #<----changed from w to a
                    #header = " $CONTRL SCFTYP=RHF RUNTYP=OPTIMIZE $end" + "\n" + " $BASIS GBASIS=STO NGAUSS=3 $END" + "\n" + " $SYSTEM MWORDS=250 $END" + "\n" + " $DATA" + "\n" + "CY_NEW_" + "\n" + "C1" + "\n"
                    SCFTYP = self.SCFTYP.currentText()
                    
                    runtypeIndex = self.runtype.currentIndex()
                    if runtypeIndex == 0:
                        runType = "ENERGY"
                    elif runtypeIndex == 1:
                        runType = "OPTIMIZE"
                    
                    NGAUSSIndex = self.NGAUSS.currentText()
                    
                    commentText = self.commentLine.text()
                    
                    first_line = " $CONTRL SCFTYP="+ SCFTYP + " RUNTYP="+ runType + " $End" + "\n"
                    second_line = " $BASIS GBASIS=STO NGAUSS=" + NGAUSSIndex + " $END" + "\n"
                    third_line = " $SYSTEM MWORDS=250 $END" + "\n"
                    fourth_line = " $DATA" + "\n"
                    fifth_line = commentText + "\n"
                    
                    #check if there is a symtery group used, if so add that to the input file
                    symmetry_group = self.symmetryLine.text()
                    if symmetry_group == "":
                        sixth_line = "C1" + "\n"
                    else:
                        sixth_line = symmetry_group + "\n"
                    
                    seventh_line = " $END"
                    
                    f.write(first_line)
                    f.write(second_line)
                    f.write(third_line)
                    f.write(fourth_line)
                    f.write(fifth_line)
                    f.write(sixth_line)
                    f.write(seventh_line)
                    f.close()
                   
                    self.write_atoms(filepath_X, filename_X, origin)
                   
                    os.chdir(filepath_X)

                    subprocess.run(filepath_X +"rungms.bat"+ ' ' + filename_X  + ' 2022.R2.intel 1 '+ fileout_X, shell=True)                     

                    f.close()
                    
                
                self.importOptGeo()  
                SAMSON.endHolding()
        except Exception:
                    
                    traceback.print_exc(file=log)
                               
    #get predefined header to keep the GUI cleaner
    
    def importOptGeo(self):
        SAMSON.beginHolding('Import Optimized Geometry')
        log = open("C:\\Users\\Public\\gamess-64\\SAMSON_log.txt", "a")
        
        indexer = SAMSON.getNodes('n.t a')                # returns all atom nodes
        
        atom_geometries_in = []
        atom_number_q =  1
        with open('C:\\Users\\Public\\gamess-64\\out.out', "r") as optimization_out_file:
            OptGeo_lines = optimization_out_file.readlines()
        
            is_negative = False
        
            EQG = "EQUILIBRIUM GEOMETRY LOCATED"
            strA = ""
        
            ERROR_1 = "THE GEOMETRY SEARCH IS NOT CONVERGED!"
            ERROR_2 = "-ABNORMALLY-"
        
            # setting flag and index to 0
            flag = 0
        
            # Loop through the file line by line
        
            for count, line in enumerate(OptGeo_lines):  
        
                if line.find(ERROR_1) > -1:
                    log.write(ERROR_1)
                    break
               
                if line.find(ERROR_2) > -1:
                    log.write(ERROR_2)
                    break                
        
                if line.find(EQG) > -1:
                    count_step = 4
                    first_atom_cordinate_line = count + count_step                                      
                    #print(first_atom_cordinate_line)
                    
            another_cordinate = True
            
            while another_cordinate == True:
                Coorindates = OptGeo_lines[first_atom_cordinate_line]
                #print(Coorindates)
        
                xyz_Coorindates_in = Coorindates.split()
                #print(atom_number_q, xyz_Coorindates_in)
        
                #atom_geometries_in.append(atom_number_q) DOESNT SEEM NECESSARY, LEAVES EXTRA NUMBER
        
                for all_coordinates in range(len(xyz_Coorindates_in)):
                    atom_geometries_in.append(xyz_Coorindates_in[all_coordinates])
                    #print(atom_geometries_in)
                    
                first_atom_cordinate_line = first_atom_cordinate_line + 1
                atom_number_q = atom_number_q + 1
                if len(xyz_Coorindates_in) == 0:
                    another_cordinate = False
            optimization_out_file.close()    
            
        atom_geometries_in.reverse() #necessary to match the SAMSOM index order and the sequence they are written in the GAMESS output file. 
        
        print(atom_geometries_in)
        
        X_index = 0
        Y_index = 1
        Z_index = 2
        
        positions = []
        
        for atom in range(0, indexer.size):
            x_cor = float((atom_geometries_in[X_index]))
            y_cor = float((atom_geometries_in[Y_index]))
            z_cor = float((atom_geometries_in[Z_index])) 
        
            position = Type.position3(Quantity.angstrom(x_cor), Quantity.angstrom(y_cor), Quantity.angstrom(z_cor))
            positions.append(position)                                                  
        
            myAtom = indexer[atom]
        
            myAtom.setX(position.x)
            myAtom.setY(position.y)
            myAtom.setZ(position.z)
        
            X_index = X_index + 5
            Y_index = Y_index + 5
            Z_index = Z_index + 5                      
        
        SAMSON.endHolding()
    
    
    def getfile(self):
        try:
            
            fname, _ = QFileDialog.getOpenFileName(self, 'Open file', 'C:\\',"Input files (*.ini)")
            self.input_filename = fname

            # [DM] Create a QFileInfo object for the file
            file_info = QFileInfo(self.input_filename)
            # Access various properties of the file
            self.file_name_label.setText(file_info.fileName())
            #self.file_path_label.setText(file_info.filePath())
        except Exception as e: 
            # [DM] Log the exception
            logging.exception("An error occurred")
            pass
    
    def switchInputType(self):
        state_1 = self.useInputFile.isChecked()
        
        if state_1 > 0:
            self.btnInput.setEnabled(True)
            self.NGAUSS.setEnabled(False)
            self.runtype.setEnabled(False)
            self.SCFTYP.setEnabled(False)
            self.usesymBox.setEnabled(False)
            self.symmetryLine.setEnabled(False)
            self.commentLine.setEnabled(False)
        else:
            self.btnInput.setEnabled(False)
            self.NGAUSS.setEnabled(True)
            self.runtype.setEnabled(True)
            self.SCFTYP.setEnabled(True)
            self.usesymBox.setEnabled(True)
            self.symmetryLine.setEnabled(True)
            self.commentLine.setEnabled(True)
    
    
    def toggleGroupLine(self):  
        state_2 = self.usesymBox.isChecked()
        
        if state_2 > 0:
            self.symmetryLine.setEnabled(True)
            
        else:
            self.symmetryLine.setEnabled(False)  
            
if __name__ == '__main__':

    # create and show the displacer

    runGAMESS = RunGAMESS()
    runGAMESS.show()
