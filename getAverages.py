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
from ScriptsCOM import matched_df,append_one_av,DataFrame,load





def get_running_averages(df,averages = [100,500,1000,5000,10000,50000]):
    vsa.on_screen.restart()
    for av in averages:
        append_one_av(av)
    return df

    
def restart(*args):
    return args[0].do_restart()

def manual(*args):
    return args[0].do_manual()
    
    
class Loggerdataset(dt.DataSet):
    manual = di.ButtonItem("take data manually",manual)
    save = di.BoolItem("log data")
    next = di.IntItem("next average number",default = 100)
    add = di.IntItem("once reached, add",default = 0)
    mult = di.IntItem("once reached, multiply by",default = 2)
    filename = di.FileSaveItem("append data to h5 file")
    restart = di.ButtonItem("restart",restart)
    
    def do_restart(self):
        self.parent.start()
        
    def do_manual(self):
        self.parent.manual()
    
    #retrace = di.ButtonItem("retrace",retrace)

class LoggerDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("Data Logger")
        self.groupbox1 = DataSetEditGroupBox("Parametres de lock",Loggerdataset,show_button = False)   
        self.groupbox1.dataset.parent = self
        self.values = self.groupbox1.dataset
        self.groupbox1.dataset.parent = self
        lay = QVBoxLayout()
        lay.addWidget(self.groupbox1)
        self.setLayout(lay)
        self.resize(800,300)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.log)
        #self.timer.timeout.connect(self.update_values)
        self.timer.setInterval(100) #ms
        self.show()
    
    def transform_number(self):
        self.values.next = self.values.next*self.values.mult + self.values.add
        self.groupbox1.get()
    
    def log(self):
        self.groupbox1.set()
        if not vsa.on_screen.meas_done():
            return
        if vsa.on_screen.current_average()<self.values.next:
            vsa.on_screen.resume()
            return
        if self.values.save:
            self.manual()
        else:
            vsa.on_screen.resume()
        self.transform_number()
        #vsa.on_screen.set_average(self.values.next)
        

    def manual(self):
        vsa.on_screen.pause()
        try:
            df = load(self.values.filename)
        except IOError:
            df = matched_df()
        append_one_av(df)
        df.save(self.values.filename)
        vsa.on_screen.resume()
        
    
    def start(self):
        print "starting"
        vsa.on_screen.set_average(self.values.next)
        vsa.on_screen.restart()
        self.timer.start()
        
        
        
        
if __name__ == "__main__":
    from guidata import qapplication
    app = qapplication()
    l = LoggerDialog()
    app.exec_()