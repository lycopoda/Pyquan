import numpy as np
import sys
import noise_reduction as noise

def baseline_poly(x,y, window=100, deg=3):
    '''fit polynomal function through minimum values in each window.
    window=number of windows (default = 100)
    deg=order of polynomal function (default=3)
    '''
    #issue: zero artefacts cause trouble in setting base line.
    #solution: ignore individual zero's
    #did not solve, also low values causing problems
    #solution: noise reduction for y values
    y = noise.savgol(y, 5)
    try:
        window = int(window)
    except:
        print('ERROR: value for window ({0} is not an integer'.\
              format(window))
        sys.exit(2)
    if max(x) < window:
        print('x range not longer than window size, \
              no baseline correction applied.')
        return y
    x_min = []
    y_min = []
    for i in range(window,len(x)-1):
        y_slice = y[i-window:i]
        idx_min = y_slice.argmin() + i-window
        x_min.append(x[idx_min])
        y_min.append(y[idx_min])
    x_min.append(x[-1])
    y_min.append(y[-1])
    y_min = np.array(y_min)
    par = np.polyfit(x_min, y_min, deg)
    bsl = np.polyval(par,x)
    bsl[bsl<0] = 0.
    return bsl
    
