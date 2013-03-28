from lock import *

scanCoh(nP = 11, span = 1e-7):
    setPoint = arange(-span/2., span/2., nP)
    for point in setPoint:
        lock()