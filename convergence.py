from myPandas import *
from hardware import vsa
import ScriptsCOM
from numpy import *
widths =[1e3,1e4,1e5]
styles = ["r.","b.","g."]
subs = [411,412,413]

try2 = ScriptsCOM.load_safe("0001_tryingHDFsotre/long_average.h5")

summary = DataFrame()
figure("Convergence of correlations")
for width,style,sub in zip(widths,styles,subs):
    df = DataFrame()
    for center in arange(0.9e6,1.8e6,width):
        data = ScriptsCOM.calculate_correl(try2,center,center+width)
        data.name = "center %f"%center    
        df = df.new_col_or_df(data.abs())
    s = df.transpose().mean()
    s.name = width
    summary = summary.new_col_or_df(s)
    subplot(sub,title = 'span = ' + str(width))
    df.plot(ax=gca(),style = style,ms = 1)
    ax = gca()
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend().set_visible(False)
    draw()
    
subplot(414,title = "average")
summary.plot(ax = gca())
ax = gca()
ax.set_xscale("log")
ax.set_yscale("log")
draw()
show()