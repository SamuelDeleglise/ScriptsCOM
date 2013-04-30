from lock import *
from HDnavigator import *
from myPandas import *
from time import sleep
import pandas
from hardware import vsa
from pandas.stats.moments import rolling_mean,rolling_apply
from numpy import isnan,array

def correlations(name = False):
    df = vsa.data(["Spectrum1","Spectrum2","Cross Spectrum"])
    coh = df["Cross Spectrum"]/(df["Spectrum1"]*df["Spectrum2"])
    val = (coh[1360000.:1400000.].real).mean() + 1j*(coh[1360000.:1400000.].imag).mean()
    if name : df.saveAsh5(next(name))
    return df, val
    

#Sshot = (dfShot[1200000.0:1400000].mean())**2
#Smod = 0.08**2
#Csmod = df["Cross Spectrum"][1400000.0:1400100.0].mean()
#CsRPN = Csmod*Sshot/Smod




def get_numaverages(df):
    res = set([int(col.rsplit('_',1)[-1]) for col in df.columns])
    res = list(res)
    res.sort()
    return res

def remove_mech_mode(df,thermal_noise = "Spectrum2_007575",window = 1000,exclude_window = 1000,thresholddiff = 3e-8):
    filtered = df.data[thermal_noise][(df[thermal_noise] - pandas.rolling_mean(df[thermal_noise].data,1000,center = True)).data<0.2e-7]    
    #filtered = filtered.rename(lambda x:"filtered_"+x)
    def clean_around(table):
        if isnan(table).any():
            return nan
        else:
            return table[len(table)/2]
    filtered.name = "filtered"
    df.join(filtered)
    filtered = df["filtered"]
    filtered = rolling_apply(filtered.data,exclude_window,clean_around,center = True)
    
    dfnew = DataFrame(df[-isnan(filtered)])
    del dfnew["filtered"]
    return dfnew


def calculate_correl(df,fStart,fStop):
    fStart=float(fStart)
    fStop=float(fStop)
    data=[]
    num_av = get_numaverages(df)
    m = df[fStart:fStop]
    for av in num_av:
        coh = m["Cross Spectrum_%06i"%av]/(m["Spectrum1_%06i"%av]*m["Spectrum2_%06i"%av])
        coh=coh.mean()
        data+=[coh]
    return pandas.Series(data,index = num_av)

def calculate_cross(df,fStart,fStop):
    fStart=float(fStart)
    fStop=float(fStop)
    data=[]
    num_av = get_numaverages(df)
    m = df[fStart:fStop]
    for av in num_av:
        coh = m["Cross_Spectrum_%06i"%av]/df["Cross_Spectrum_%06i"%av].meta.Frequency.ResBW
        coh=coh.mean()
        data+=[coh]
    return pandas.Series(array(data),index = array(num_av))
            
def matched_df():
    df = vsa.data(["Spectrum1"])
    del df["Spectrum1"]
    return df




def save_running_averages(filename,averages = [2**n for n in range(16)]):
    from pandas import HDFStore
    f = HDFStore(filename)
    df = matched_df()
    vsa.on_screen.restart()
    try:
        for i in averages:
            append_one_av(df,i)
            f["data"] = df
            f.flush()
    except KeyboardInterrupt:
        f.close()

    

def append_one_av(df):
    #if not isinstance(av,int):
    #    raise ValueError("num averages should be integer")
    #vsa.on_screen.wait_average(av)
    dft = vsa.data(["Spectrum1","Spectrum2","Cross_Spectrum"])
    real_av = vsa.on_screen.current_average()
    df["Spectrum1_%06i"%real_av] = dft["Spectrum1"]
    df["Spectrum2_%06i"%real_av] = dft["Spectrum2"]
    df["Cross_Spectrum_%06i"%real_av] = dft["Cross_Spectrum"]
    return df


def get_running_averages(df,averages = [100,500,1000,5000,10000,50000]):
    vsa.on_screen.restart()
    for av in averages:
        append_one_av(av)
    return df

def moy():
    df=0
    try:
        i=0
        while(i<=5000):
#            print('waiting')
            if vsa.on_screen.meas_done(0):
                print('acquiring')
                dft=vsa.data(["Spectrum1","Spectrum2","Cross Spectrum"])
                if i is 0:
                    df=DataFrame(dft)
                else:
                    for col in dft:
                        newName=col+'_'+str(i)
                        serie = dft[col]
                        serie.name=newName
                        df = df.join(serie)
                i+=1
                vsa.on_screen.restart()
            else:
                sleep(1)
    except KeyboardInterrupt:
        print 'Bye'
        return df
    return df

def c_mean(z):
    return z.real.mean()+1j*z.imag.mean()
        
def moyDf(df,fStart,fStop):
    fStart=float(fStart)
    fStop=float(fStop)
    data=[]
    m=DataFrame({"Cross Spectrum":df["Cross Spectrum"][fStart:fStop],
                   "Spectrum1":df["Spectrum1"][fStart:fStop], 
                   "Spectrum2":df["Spectrum2"][fStart:fStop]})
    m=m*0
    for j,i in enumerate(df):
        type=i.rsplit('_',1)[0]
        m[type]+=df[i][fStart:fStop]
        if type == "Spectrum2":
            coh = m["Cross Spectrum"]/(m["Spectrum1"]*m["Spectrum2"])
            coh=coh * j/3
            coh=c_mean(coh)
            data+=[coh]
    return data