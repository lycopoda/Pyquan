import numpy as np


def baseline_poly(x,y, window=100, deg=3):
    '''fit polynomal function through minimum values in each window.
    Give window size (default = 100 time steps)'''
    import numpy as np
    if max(x) < window:
        print 'x range not longer than window size, no baseline correction applied.'
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
    
