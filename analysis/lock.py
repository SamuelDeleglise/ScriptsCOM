from hardware import afg
from hardware import vsa
import time

def lock(setPoint = 0., gain = -1.0e5, AFG = "AFG_CHI", delai_s = 1.0, meas = 1):
    print 'acquiring afg...'
    a=afg.AFG3102(AFG)
    a.setChannel(2)
    print 'afg acquired'
    gain_num = gain*delai_s
    val = a.getOffset()
    while( not( vsa.on_screen.meas_done(0) ) ):
        print 'waiting...'
        time.sleep(delai_s)
        df = vsa.data(['Cross Spectrum'],measurement=meas)
        center=df['Cross Spectrum'].real.size/2
        curPoint=df['Cross Spectrum'].real[center]
        val = val+(curPoint - setPoint)*gain_num
        print val
        a.setOffset(val,ch = 2)