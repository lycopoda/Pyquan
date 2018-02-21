import sys
import numpy as np

def median(x):
    '''The median of a list of numbers (integers or floats) is returned.'''
    sorts = sorted(x)
    length =len(sorts)
    if length ==1:
        return x[0]
    elif not length % 2:
        return (sorts[length // 2] + sorts[length //2 -1]) /2.0
    else:
        return sorts[length //2]


def linreg(x,y, slope=True):
    '''linreg returns the slope and intercept of a set of data (x,y).
       If slope is not True, slope is set at 1.'''
    linfit = LinFit(x, y, slope)
    return linfit.lin_fit()

class LinFit(object):
    def __init__(self, x,y, slope):
        self._x = x
        self._y = y
        self._slope = slope 

    def lin_func_slope_var(self, x, *pars):
        rc, ic = pars
        return rc*x + ic

    def lin_func_slope_fix(self, x, ic):
        return x+ic

    def lin_fit(self):
        from scipy.optimize import curve_fit
        if self._slope == 'yes':
            pars=[1.0,0.]
            popt, pcov = curve_fit(self.lin_func_slope_var, self._x, 
                                   self._y, pars)
            rc, ic  = popt
        else:
            rc = 1.0
            ic = 0.0
            popt, pcov = curve_fit(self.lin_func_slope_fix, self._x, 
                                   self._y, ic)
            ic = popt[0]
        return rc, ic

    
def reg_robust(x,y, slope=True, lim=0.01):
    '''Finds a line that connects most data points within a 
       defined distance (lim*max(y)) from the line. It is highly
       robust against asymetric distributions.
       It returns the slope and intercept.'''
    rob = RobustRegression(x,y, slope, lim)
    return rob.lin_robust()

class RobustRegression(object):
    def __init__(self, x, y, slope, lim):
        self._x = x
        self._y = y
        if not len(x) == len(y):
            print('x and y should be same length in Class Regression')
            sys.exit(2)
        self._slope = slope
        self._lim = lim * max(y)
        
    def get_rc_list(self):
        self._rc_list=[]
        x_set = set()
        index_range = range(len(self._x))
        for i in index_range:
            x_set.add(i)
            for j in index_range:
                if not j in x_set and not self._x[i] == self._x[j]:
                    rc = (self._y[i]-self._y[j]) / (self._x[i] - self._x[j])
                    ic = self._y[i] - self._x[i]*rc
                    item = (i,j,rc,ic)
                    self._rc_list.append(item)
        return
        
    def get_line_list(self, item):
        rc=item[2]
        ic=item[1]
        return np.where(abs(self._x*rc+ic-self._y) < self._min)[0]

        rc = item[2]
        ic = item[3]
        idx_list = []
        for i in range(len(self._x)):
            if abs(rc*self._x[i]+ic - self._y[i]) < self._lim:
                idx_list.append(i)
        return idx_list
    
    def lin_robust(self):
        self.get_rc_list()
        line_list = []
        for i in self._rc_list:
            idx_list = self.get_line_list(i)
            line_list.append(idx_list)
        max_list = 0
        idx_line = None
        for j in line_list:
            if len(j) > max_list:
                max_list = len(j)
                idx_line = j
        x_list=[]
        y_list=[]
        for idx in idx_line:
            x_list.append(self._x[idx])
            y_list.append(self._y[idx])
        [rc, ic] = linreg(x_list, y_list, slope=self._slope)
        return rc, ic
