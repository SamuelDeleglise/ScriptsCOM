from guidata.dataset.qtwidgets import DataSetShowGroupBox, DataSetEditGroupBox
from guidata.qt.QtGui import QMainWindow, QDialog, QSplitter, QCheckBox,QHBoxLayout,QVBoxLayout
from guidata.qt.QtCore import SIGNAL, QTimer

import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di
import myguidataitems as mdi

from guiqwt.plot import CurveWidget
from visa import VisaIOError
import numpy as np
from guiqwt.builder import make
from hardware import vsa
from pandas import HDFStore
from ScriptsCOM import matched_df,append_one_av

def append_one_av(df,av):
    if not isinstance(av,int):
        raise ValueError("num averages should be integer")
    vsa.on_screen.wait_average(av)
    dft = vsa.data(["Spectrum1","Spectrum2","Cross Spectrum"])
    real_av = vsa.on_screen.current_average()
    df["Spectrum1_%06i"%real_av] = dft["Spectrum1"]
    df["Spectrum2_%06i"%real_av] = dft["Spectrum2"]
    df["Cross Spectrum_%06i"%real_av] = dft["Cross Spectrum"]
    return df




def get_running_averages(df,averages = [100,500,1000,5000,10000,50000]):
    vsa.on_screen.restart()
    for av in averages:
        append_one_av(av)
    return df

    

    
    
class Loggerdataset(dt.DataSet):
    save = di.BoolItem("log data")
    
    next = di.IntItem("next average number",default = 100)
    add = di.IntItem("once reached, add",default = 0)
    mult = di.IntItem("once reached, multiply by",default = 2)

    filename = di.FileSaveItem("append data to h5 file")

#    log = di.ButtonItem("log",log)
    

    #retrace = di.ButtonItem("retrace",retrace)

class LoggerDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("Data Logger")
        self.groupbox1 = DataSetEditGroupBox("Parametres de lock",Loggerdataset,show_button = False)   
        self.groupbox1.dataset.parent = self
        self.values = self.groupbox1.dataset
        lay = QVBoxLayout()
        lay.addWidget(self.groupbox1)
        self.setLayout(lay)
        self.resize(800,300)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.log)
        #self.timer.timeout.connect(self.update_values)
        self.timer.setInterval(100) #ms
        self.timer.start()
        self.show()
    
    def transform_number(self):
        self.values.next = self.values.next*self.values.mult + self.values.add
        self.groupbox1.get()
    
    def log(self):
        self.groupbox1.set()
        if self.values.save:
            if vsa.on_screen.current_average()>=self.values.next:
                f = HDFStore(self.values.filename)
                try:
                    df = f["data"]
                except KeyError:
                    df = matched_df()
                append_one_av(df,self.values.next)
                f["data"] = df
                f.close()
                self.transform_number()
        
if __name__ == "__main__":
    from guidata import qapplication
    app = qapplication()
    l = LoggerDialog()
    app.exec_()