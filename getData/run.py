from PyQt4 import QtCore, QtGui
from pyinstruments.pyhardwaredb import instrument
from pyinstruments.curvestore import models
from time import sleep

vsa = instrument("vsa")

class runCOM(QtGui.QWidget):
    def __init__(self, default_sleep=2, default_sleep_lock_time=1000, default_gain=1):
        super(runCOM, self).__init__()
        self.tags = [self.get_current_tag()]
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(default_sleep)
        self.timer.timeout.connect(self.take_data)
        
        self.timer_lock = QtCore.QTimer()
        self.timer_lock.setSingleShot(True)
        self.timer_lock.setInterval(default_sleep_lock_time)
        self.timer_lock.timeout.connect(self.lock)
        
        self.button_start = QtGui.QPushButton("Start")
        self.button_start.clicked.connect(self.button_start_clicked)
        
        self.button_stop = QtGui.QPushButton("Stop")
        self.button_stop.clicked.connect(self.button_stop_clicked)
        
        self.label_acq = QtGui.QLabel("Acquisition")
        
        self.label = QtGui.QLabel('sleep time (s)')
        self.sleep_time_box = QtGui.QSpinBox() 
        self.sleep_time_box.setMaximum(int(1e9))
        self.checkbox_auto_sleep = QtGui.QCheckBox("auto")
        
        self.checkbox_restart = QtGui.QCheckBox("Restart averaging on start")
        
        self.label_lock_time = QtGui.QLabel('lock duty time (ms)')
        self.sleep_time_lock_box = QtGui.QSpinBox() 
        self.sleep_time_lock_box.setMaximum(int(1e9))
        self.sleep_time_lock_box.setValue(default_sleep_lock_time)
        
        self.label_lock = QtGui.QLabel("Lock")
        
        self.power_label = QtGui.QLabel('input power (mW)')
        self.power_box = QtGui.QSpinBox() 
        
        self.gain_label = QtGui.QLabel('gain')
        self.gain_box=QtGui.QSpinBox()
        self.gain_box.setValue(default_gain)
        
        self.button_start_lock = QtGui.QPushButton("Start")
        self.button_start_lock.clicked.connect(self.button_start_lock_clicked)
        
        self.button_stop_lock = QtGui.QPushButton("Stop")
        self.button_stop_lock.clicked.connect(self.button_stop_lock_clicked)
        
        self.hlay1 = QtGui.QHBoxLayout()
        self.hlay1.addWidget(self.label_acq)
        self.hlay1.addStretch(1)
        self.hlay1.addWidget(self.button_start)
        self.hlay1.addWidget(self.button_stop)
        
        
        self.hlay5 = QtGui.QHBoxLayout()
        self.hlay5.addStretch(1)
        self.hlay5.addWidget(self.checkbox_restart)
        
        self.hlay2 = QtGui.QHBoxLayout()
        self.hlay2.addWidget(self.label)
        self.hlay2.addWidget(self.sleep_time_box)
        self.hlay2.addStretch(1)
        self.hlay2.addWidget(self.checkbox_auto_sleep)

        self.hlay3 = QtGui.QHBoxLayout()
        self.hlay3.addWidget(self.label_lock_time)
        self.hlay3.addWidget(self.sleep_time_lock_box)
        self.hlay3.addStretch(1)
        self.hlay3.addWidget(self.gain_label)
        self.hlay3.addWidget(self.gain_box)

        self.hlay4 = QtGui.QHBoxLayout()
        self.hlay4.addWidget(self.power_label)
        self.hlay4.addWidget(self.power_box)
        
        self.hlay6 = QtGui.QHBoxLayout()
        self.hlay6.addWidget(self.label_lock)
        self.hlay6.addStretch(1)
        self.hlay6.addWidget(self.button_start_lock)
        self.hlay6.addWidget(self.button_stop_lock)

        self.v_lay = QtGui.QVBoxLayout()
        self.v_lay.addLayout(self.hlay1)
        self.v_lay.addLayout(self.hlay5)
        self.v_lay.addLayout(self.hlay2)
        self.v_lay.addLayout(self.hlay6)
        self.v_lay.addLayout(self.hlay3)
        self.v_lay.addLayout(self.hlay4)
        self.setLayout(self.v_lay)
        self.setWindowTitle("runCOM")
        
        self.sleep_time = default_sleep
        self.show()
            
    def button_start_clicked(self):
        if self.isRestart:
            vsa.restart()
            vsa.pause()
            sleep(5)
            vsa.pause()
        self.take_data()
        self.timer.setInterval(1000*(self.sleep_time))
        self.timer.start()
        
    def button_stop_clicked(self):
        self.timer.stop()
        
    def button_start_lock_clicked(self):
        self.lock()
        self.timer_lock.setInterval(self.sleep_lock_time)
        self.timer_lock.start()
        
    def button_stop_lock_clicked(self):
        self.timer_lock.stop()
            
    def take_curve(self, label):
        vsa.active_label = label
        curve = vsa.get_curve()
        curve.tags+= self.tags
        curve.params["name"] = curve.params["data_name"] + "_" +\
                                str(curve.params["current_average"])
        curve.save()
        
    def take_data(self):
        print 'taking data'
        vsa.pause()
        self.take_curve('A')
        self.take_curve('B')
        self.take_curve('C')
        self.take_curve('F')
        self.take_curve('G')
        if self.isAuto:
            self.sleep_time=self.sleep_time*2
        self.timer.setInterval(1000*self.sleep_time)
        vsa.resume()
        self.timer.start()
        
    @property
    def sleep_time(self):
        return self.sleep_time_box.value()
    
    @sleep_time.setter
    def sleep_time(self, val):
        self.sleep_time_box.setValue(val)
        
    @property
    def sleep_lock_time(self):
        return self.sleep_time_lock_box.value()
    
    @sleep_lock_time.setter
    def sleep_lock_time(self, val):
        self.sleep_time_lock_box.setValue(val)
        
    @property
    def gain(self):
        return self.gain_box.value()
    
    @gain.setter
    def gain(self, val):
        self.gain_box.setValue(val) 

    def get_current_tag(self):
        existing = models.Tag.objects.filter(name__startswith="runCOM")
        num_max = 0
        for tag in existing:
            num_str = tag.name.split("/")[-1]
            try:
                num = int(num_str)
            except ValueError:
                pass
            else:
                num_max = max(num_max, num)
        return "runCOM/%04i"%(num_max+1)

    @property
    def isAuto(self):
        return bool(self.checkbox_auto_sleep.checkState())

    @isAuto.setter
    def isAuto(self, val):
        return self.checkbox_auto_sleep.setCheckState(2*val)
    @property
    def isRestart(self):
       return bool(self.checkbox_restart.checkState())
    
    @isRestart.setter
    def isRestart(self, val):
       return self.checkbox_restart.setCheckState(2*val)

    def take_detuning(self):
        vsa.active_label = 'G'
        curve = vsa.get_curve()
        
    def lock(self):
        print "Locking"
        self.take_detuning()
        self.timer_lock.setInterval(self.sleep_lock_time)
        self.timer_lock.start()