import numpy as np
from scipy.signal import argrelextrema
import sys

class Pars:
    '''collects parameter values for peak of interest and possible overlaping peaks'''
    
    def __init__(self, info):
        self._p_order = info.p_order()
        self._thresh = info.thresh()

    def get_param(self, x,y,RT):
        '''Collect parameter estimates from time(x)/intensity(y) data.
        Return parameter dictionary for left int and right peak, plus the slice
        in x/y data for the peak'''
        self._x = np.array(x)
        self._y = np.array(y)
        self._RT = RT
        self._range_peak = {}
        self._left_min =None
        self._right_min = None
        self._left_max = None
        self._right_max = None
        pars = {}
        x_peak = None
        y_peak = None
        max_list = (argrelextrema(self._y, np.greater, order=self._p_order)[0]).astype(int).tolist()#gives index for maxima
#define peak of interest
        if max_list:
    #max closest to RT is peak of interest
            self._idx_int = max_list[(np.abs(self._x[max_list]-self._RT)).argmin()]
    #consider only peak with minimum distance from peak of interest 
    #to avoid deconvoluting noise of the peak of interest
    #select indexes for intensity below threshold:
            min_list = (np.where(self._y < self._thresh*self._y[self._idx_int])[0]).astype(int).tolist()
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

    @property
    def xy_int(self):
        start = self._range_peak['int'][0]
	end = self._range_peak['int'][2]
	x = self._x[start:end]
	y = self._y[start:end]
	return x,y

    def func_truncate(self):
        if self._range_peak['right'][0] and self._range_peak['left'][2]:
            start_idx = self._range_peak['left'][0]
            end_idx = self._range_peak['right'][2]
            start_idx, end_idx = self.correct_range(start_idx, end_idx, n=12)
        elif self._range_peak['right'][0]:
            start_idx = self._range_peak['int'][0]
            end_idx = self._range_peak['right'][2]
            start_idx, end_idx =self.correct_range(start_idx, end_idx, n=8)
        elif self._range_peak['left'][0]:
            start_idx = self._range_peak['left'][0]
            end_idx = self._range_peak['int'][2]
            start_idx, end_idx = self.correct_range(start_idx, end_idx, n=8)
        else:
            start_idx = self._range_peak['int'][0]
            end_idx = self._range_peak['int'][2]
            start_idx, end_idx = self.correct_range(start_idx, end_idx, n=4)
        x_peak = []
        y_peak = []
        for i in range(start_idx,end_idx):
            x_peak.append(self._x[i])
            y_peak.append(self._y[i])
        return np.array(x_peak), np.array(y_peak)
            
    def correct_range(self, start, end, n=4):
        dif = end -start
        if dif <= n:
            start = start - dif/2 - 1
            end = end + dif/2 + 1
        return start, end

    def func_pars(self, peak):
        pars=[]
        if peak[0] !=None:   
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

    def local_min(self, start, end):
        intensity = []
	for i in range(len(self._x)):
	    if start <= i <= end:
	        intensity.append((i, self._y[i]))
        try:
	    valley = min(intensity, key = lambda t: t[1])[0]
	except:
	    valley = int((start+end)/2)   
	return valley

    def func_left_peak(self):
        start_left=None
        idx_left=None
        end_left=None
        end_left_value=None
        if self._left_max and self._left_min:
            if max(self._left_max)> max(self._left_min):
                idx_left = max(self._left_max)
                start_left = self.func_left_start()
                end_left = self.local_min(idx_left, self._idx_int)
        self._range_peak['left'] = (start_left, idx_left, end_left)
        return

    def func_right_peak(self):
        start_right=None
        idx_right=None
        end_right=None
        start_right_value=None
        if self._right_max:
            if self._right_min:
                if self._right_max[0] < self._right_min[0]:
                    idx_right = self._right_max[0]
                    end_right = self.func_right_end(idx_right)
            else:
                idx_right = self._right_max[0]
                end_right = self.func_right_end(idx_right)
            if idx_right:
                start_right = self.local_min(self._idx_int, idx_right)
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


