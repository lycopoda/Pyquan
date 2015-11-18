import numpy as np
import sys


def correct(y, info_dict):
    smooth = info_dict['smooth']['method']
    if smooth:
        import pyquan_smooth as sm
        window = info_dict['smooth']['window']
        if smooth == 'savgol':
            order = info_dict['smooth']['order']
            intensity = sm.savgol(y, window, order)
        elif smooth == 'mov_av':
            window_type = info_dict['smooth']['type']
            intensity =  sm.run_average(y, window_len=window, window=window_type)
        else:
            print 'no smoothing applied'
    baseline = info_dict['bsl']['method']
    if baseline:
        import pyquan_bsl as bsl
        reload(bsl)
        if baseline == 'quant_reg':
            quantile = info_dict['bsl_info']['quantile']
            intensity = bsl.quant_reg(y, quantile)
        elif  baseline ==  'min_reg':
            intensity = bsl.min_reg(y)
        else:
            print 'no baseline correction applied' 
    return y
    


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
    the values of the time history of the signal.
    window_size : int
    the length of the window. Must be an odd integer number.
    order : int
    the order of the polynomial used in the filtering.
    Must be less then `window_size` - 1.
    deriv: int
    the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
    the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    from math import factorial
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

def baseline(y):
    return y-min(y)
    

def baseline_linreg(x, y):
    #baseline correction, based on left and right minimum
    x=np.array(x)
    y=np.array(y)
    y_dict = {}
    y_dict['left'] = y[:int(len(y)/2)]
    y_dict['right'] = y[int(len(y)/2):]
    min_dict = {}
    for i in y_dict:
        min_dict[i] = min((value, index) for (index, value) in enumerate(y_dict[i]))
    #calculate correction line parameters
    a = (min_dict['right'][0]-min_dict['left'][0]) / (x[min_dict['right'][1]+int(len(y)/2)] - x[min_dict['left'][1]])
    b = y[min_dict['left'][1]] - a*x[min_dict['left'][1]]
    y = y - a*x-b
    return y

#setup for alternative baseline correction (doesn't work yet!)
def baseline_quant_linreg(x,y):
    import statsmodels.api as sm
    part = int(len(x)/3)
    y=np.array(y)
    x=np.array(x)
    idx_list=np.argsort(y)[:part]
    x_sort = x[idx_list]
    x_sort=sm.add_constant(np.array(x_sort))
    y_sort = y[idx_list]
    #linear regression
    rlm_model = sm.RLM(y_sort,x_sort, M=sm.robust.norms.HuberT()).fit()
    bsl=x*rlm_model.params[0]+rlm_model.params[1]
    y_new=y-bsl
    return y_new        

def baseline_quantile(x,y):
    from statsmodels.regression.quantile_regression import QuantReg
    model = QuantReg(x,y).fit(0.1)
    a1=model.params[0]
    a2=model.params[1]
    y=y*a1+a2
    return y
                
                                    

class Pars:
    '''collects parameter values for peak of interest and possible overlaping peaks'''
    def __init__(self, x, y, RT):
        self._x = np.array(x)
        self._y = np.array(y)
        self._RT = RT
        self._idx_int = ()
        self._left_min = []
        self._right_min = []
        self._left_max = []
        self._right_max = []
        self._range_peak = {}
        

    def peak_pars(self, p_order=3, threshold=0.3):
        from scipy.signal import argrelextrema
#find peak closest to RT
    #select maxima
        pars = {}
        x_peak = None
        y_peak = None
        max_list = (argrelextrema(self._y, np.greater, order=p_order)[0]).astype(int).tolist()#gives index for maxima
#define peak of interest
        if max_list:
    #max closest to RT is peak of interest
            self._idx_int = max_list[(np.abs(self._x[max_list]-self._RT)).argmin()]
    #consider only peak with minimum distance from peak of interest 
    #to avoid deconvoluting noise of the peak of interest
    #select indexes for intensity below threshold:
            min_list = (np.where(self._y < threshold*self._y[self._idx_int])[0]).astype(int).tolist()
    #consider only maxima with a minimum distance from peak of interest,
    #divide max in right and left maxima
            self._left_max = [s for s in max_list if s < self._idx_int]
            self._right_max = [s for s in max_list if s > self._idx_int]
            if min_list:
                self._left_min = [s for s in min_list if s < self._idx_int]
                self._right_min = [s for s in min_list if s > self._idx_int]
    #check for convoluting peaks
            self.func_left_peak()
            self.func_right_peak()
            self.func_int_peak()
            for i in self._range_peak:
                pars[i] = self.func_pars(self._range_peak[i])
#truncate time range of interest
                x_peak, y_peak = self.func_truncate()
        return pars, x_peak, y_peak

    def func_truncate(self):
        if self._range_peak['left'][0]:
            start_idx = self._range_peak['left'][0]
        else:
            start_idx = self._range_peak['int'][0]
        if self._range_peak['right'][2]:
            end_idx = self._range_peak['right'][2]
        else:
            end_idx = len(self._x)
        x_peak = []
        y_peak = []
        for i in range(start_idx,end_idx):
            x_peak.append(self._x[i])
            y_peak.append(self._y[i])
        return np.array(x_peak), np.array(y_peak)
    

    def func_pars(self, peak):
        pars=[]
        if peak[0]:   
            int_B = self._x[peak[2]] - self._x[peak[1]]
            int_A = self._x[peak[1]] - self._x[peak[0]]
            a2 = np.sqrt(-1/(2*np.log(0.1))*(int_B*int_A))
            a3 = -1./(np.log(0.1))*(int_B-int_A)
            a0 = self._y[peak[1]]
            pars=[a0,self._x[peak[1]], a2,a3]
        else:
            pars=[(),(),(),()]
        return pars

    def func_int_peak(self):
        if self._range_peak['left'][2]:
            start_int = self._range_peak['left'][2]
        elif self._left_min:
            start_int = self._left_min[-1]
        else:
            start_int = 0
        if self._range_peak['right'][0]:
            end_idx = self._range_peak['right'][0]
        elif self._right_min:
            end_idx = self._right_min[0]
        else:
            end_idx = len(self._x)-1
        self._range_peak['int'] = (start_int, self._idx_int, end_idx)
        return

    def func_left_peak(self):
        start_left=None
        idx_left=None
        end_left=None
        end_left_value=None
        if self._left_max and self._left_min:
            if max(self._left_max)> max(self._left_min):
                idx_left = max(self._left_max)
                start_left = self.func_left_start()
                end_left_value = (self._x[idx_left]+self._x[self._idx_int])/2.
        if end_left_value:
            end_left = min(range(len(self._x)),key=lambda i: abs(self._x[i]-end_left_value))
        self._range_peak['left'] = (start_left, idx_left, end_left)
        return

    def func_right_peak(self):
        start_right=()
        idx_right=()
        end_right=()
        start_right_value=()
        if self._right_max:
            if self._right_min:
                if self._right_max[0] < self._right_min[0]:
                    idx_right = self._right_max[0]
                    end_right = self.func_right_end(idx_right)
            else:
                idx_right = self._right_max[0]
                end_right = self.func_right_end(idx_right)
            if idx_right:
                start_right_value = (self._x[idx_right]+self._x[self._idx_int])/2.
        if start_right_value:
            start_right = min(range(len(self._x)),key=lambda i: abs(self._x[i]-start_right_value))
        self._range_peak['right'] = (start_right, idx_right, end_right)
        return

    def func_left_start(self):
        start_left_value = ()
        if len(self._left_max)>1:
            if self._left_min:
                if self._left_min[-1]>self._left_max[-2]:
                    start_left = self._left_min[-1]
                else:
                    start_left_value = (self._x[self._left_max[-1]] + self._x[self._left_max[-2]])/2.
            else:
                start_left_value = (self._x[self._left_max[-1]] + self._x[self._left_max[-2]])/2.
        elif self._left_min:
            start_left = self._left_min[-1]
        else:
            start_left = 0
        if start_left_value:
            start_left = min(range(len(self._x)),key=lambda i: abs(self._x[i]-start_left_value))
        return start_left

    def func_right_end (self, right_idx):
        end_right_value=()
        if len(self._right_max)>1:
            if self._right_min:
                if self._right_min[0] < self._right_max[1]:
                    end_right = self._right_min[0]
                else:
                    end_right_value = (self._x[self._right_max[0]] + self._x[self._right_max[1]])/2
            else:
                end_right_value = (self._x[self._right_max[0]] + self._x[self._right_max[1]])/2
        elif self._right_min:
            end_right = self._right_min[0]
        else:
            end_right = len(self._x)-1
        if end_right_value:
            end_right = min(range(len(self._x)),key=lambda i: abs(self._x[i]-end_right_value))
        return end_right
#-------------------------------------------------------------------------------


class Fit():
    '''Deconvolute peaks, and quantify peak of interest'''
    
    def __init__(self, pars):
        self._pars = pars # after fitting, update pars; add save_image to Fit
                
    def peak_fit(self, x_fit, y_fit):
        from scipy.optimize import curve_fit
        area = None
        param = self._pars['left'] + self._pars['int'] + self._pars['right']
        indexes = [9,5,1]
        for index in indexes:
            del param[index]
        par_fit = {}
        if self._pars['int'][0]:
            try:
                if self._pars['left'][0] and self._pars['right'][0]:
                    popt, pcov = curve_fit(self.peak_int_right_left1, x_fit, y_fit, param)
                    param2 = np.insert(popt, [1,4,7], [self._pars['left'][1], self._pars['int'][1], self._pars['right'][1]])
                    popt, pcov = curve_fit(self.peak_int_right_left2, x_fit, y_fit, param2)
                    self._pars['left'] = popt[:4]
                    self._pars['int'] = popt[4:8]
                    self._pars['right'] = popt[8:]
                elif self._pars['left'][0]:
                    param = param[:6]
                    popt, pcov = curve_fit(self.peak_int_left1, x_fit, y_fit, param)
                    param2 = np.insert(popt, [1,4], [self._pars['left'][1], self._pars['int'][1]])
                    popt, pcov = curve_fit(self.peak_int_left2, x_fit, y_fit, param2)
                    self._pars['left'] = popt[:4]
                    self._pars['int'] = popt[4:]
                elif self._pars['right'][0]:
                    param = param[3:]
                    popt, pcov = curve_fit(self.peak_int_right1, x_fit, y_fit, param)
                    param2 = np.insert(popt, [1,4], [self._pars['int'][1], self._pars['right'][1]])
                    popt, pcov = curve_fit(self.peak_int_right2, x_fit, y_fit, param2)
                    self._pars['int'] = popt[:4]
                    self._pars['right'] = popt[4:]
                else:
                    param = param[3:6]
                    popt, pcov = curve_fit(self.peak_int1, x_fit, y_fit, param)
                    param2 = np.insert(popt, 1, self._pars['int'][1])
                    popt,pcov = curve_fit(self.peak_int2, x_fit, y_fit, param2)
                    self._pars['int'] = popt        
#numerical solution to estimate area of EGH, see Lan and Jorgenson, 2001
                t = np.arctan(abs(self._pars['int'][3])/self._pars['int'][2])
                epsilon = 4.-6.293724*t+9.232834*t**2-11.342910*t**3+9.123978*t**4-4.173753*t**5+0.827797*t**6
                area = self._pars['int'][0]*(self._pars['int'][2]*np.sqrt(np.pi/8)+abs(self._pars['int'][3]))*epsilon
            except RuntimeError:
                area =self.real_area(x_fit, y_fit)
        return area, par_fit
   
    def real_area(self, x_fit, y_fit):
        area = np.trapz(y_fit, x_fit)
        return area    

    def asym_peak_old(self, t, pars_it):# EGH function, see Lan and Jorgenson, 2001, J. Chromatography 915: 1-13
        a0 = float(pars_it[0])
        a1 = float(pars_it[1])
        a2 = float(pars_it[2])
        a3 = float(pars_it[3])
        f=[]
        n=()
        for time in t:
            p = (time-a1)
            if 2*a2**2+a3*p > 0:
                n = a0*np.exp(-p**2/(2*a2**2+a3*p))
            else:
                n = 0
            f.append(n)
        f=np.array(f).astype(np.float)
        return f

                      
    def asym_peak(self, t, pars_it):
        '''EGH function, see Lan and Jorgenson, 2001, J. Chromotography 915: 1-13
        Input: x-array and list of 4 parameter values'''
        a0 = float(pars_it[0]) #peak height
        a1 = float(pars_it[1]) #retention time
        a2 = float(pars_it[2]) #st dev of Gaussian
        a3 = float(pars_it[3]) #time constant of precursor exponential
        f=[]
        f=a0*np.exp(-(t-a1)**2/(2*a2**2+a3*(t-a1)))
        f[f<0]=0
        return f

    def peak_int1(self, t, *pars):
        p_int=[]
        a20 = pars[0]
        a21 = self._pars['int'][1]
        a22 = pars[1]
        a23 = pars[2]
        p_int = self.asym_peak(t, [a20, a21, a22, a23])
        return p_int

    def peak_int2(self, t, *pars):
        p_int=[]
        a20 = pars[0]
        a21 = pars[1]
        a22 = pars[2]
        a23 = pars[3]
        p_int = self.asym_peak(t, [a20,a21,a22,a23])
        return p_int

    def peak_int_left1(self, t, *pars):
        p_int=[]
        p_left=[]
        a10 = pars[0]
        a11 = self._pars['left'][1]
        a12 = pars[1]
        a13 = pars[2]
        a20 = pars[3]
        a21 = self._pars['int'][1]
        a22 = pars[4]
        a23 = pars[5]
        p_int = self.asym_peak(t, [a20, a21, a22, a23])
        p_left = self.asym_peak(t, [a10, a11, a12, a13])
        return p_int+p_left

    def peak_int_left2(self, t, *pars):
        p_int=[]
        p_left=[]
        a20 = pars[4]
        a21 = pars[5]
        a22 = pars[6]
        a23 = pars[7]
        a10 = pars[0]
        a11 = pars[1]
        a12 = pars[2]
        a13 = pars[3]    
        p_int = self.asym_peak(t, [a20,a21,a22,a23])
        p_left = self.asym_peak(t, [a10,a11,a12,a13])
        return p_int + p_left

    def peak_int_right1(self, t, *pars):
        p_int=[]
        p_right=[]
        a20 = pars[0]
        a21 = self._pars['int'][1]
        a22 = pars[1]
        a23 = pars[2]
        a30 = pars[3]
        a31 = self._pars['right'][1]
        a32 = pars[4]
        a33 = pars[5]
        p_int = self.asym_peak(t, [a20, a21, a22,a23])
        p_right = self.asym_peak(t, [a30, a31, a32,a33])
        f=p_int+p_right
        return f
    
    def peak_int_right2(self, t, *pars):
        a20 = pars[0]
        a21 = pars[1]
        a22 = pars[2]
        a23 = pars[3]
        a30 = pars[4]
        a31 = pars[5]
        a32 = pars[6]
        a33 = pars[7]
        p_int = self.asym_peak(t, [a20, a21, a22, a23])
        p_right = self.asym_peak(t, [a30, a31, a32, a33])
        return p_int+p_right
    
    def peak_int_right_left1(self, t, *pars):
        p_int=[]
        p_left=[]
        p_right=[]
        a20 = pars[3]
        a21 = self._pars['int'][1]
        a22 = pars[4]
        a23 = pars[5]    
        a10 = pars[0]
        a11 = self._pars['left'][1]
        a12 = pars[1]
        a13 = pars[2]    
        a30 = pars[6]
        a31 = self._pars['right'][1]
        a32 = pars[7]
        a33 = pars[8]    
        p_int = self.asym_peak(t, [a20,a21,a22,a23])
        p_right = self.asym_peak(t, [a30,a31,a32,a33])
        p_left = self.asym_peak(t, [a10,a11,a12,a13])
        return p_int+p_right+p_left

    def peak_int_right_left2(self, t, *pars):
        p_int=[]
        p_left=[]
        p_right=[]
        a20 = pars[4]
        a21 = pars[5]
        a22 = pars[6]
        a23 = pars[7]    
        a10 = pars[0]
        a11 = pars[1]
        a12 = pars[2]
        a13 = pars[3]    
        a30 = pars[8]
        a31 = pars[9]
        a32 = pars[10]
        a33 = pars[11]    
        p_int = self.asym_peak(t, [a20,a21,a22,a23])
        p_right = self.asym_peak(t, [a30,a31,a32,a33])
        p_left = self.asym_peak(t, [a10,a11,a12,a13])
        return p_int+p_right+p_left
        
    def save_image(self, ID, code, x, y):
        import matplotlib.pyplot as plt
        import os.path
        x = np.array(x)
        y = np.array(y)
        plt.figure()
        plt.plot(x,y)
        plt.xlabel('Time (min)')
        plt.ylabel('intensity')
        plot_name = os.path.join('{0}/images/{1}_{2}.png'.format(ID['project'], code, ID['sample']))
        for i in self._pars:
            if self._pars[i][0]:
                peak = self.asym_peak_old(x, self._pars[i])
                if i == 'int':
                    plt.plot(x, peak, 'r-')
                else:
                    plt.plot(x, peak, 'y-')
        plt.savefig(plot_name)
        plt.close()
        return
