'''This module quantify and stores the peak of interest
It needs project, sample and code info, plus the quantification info
(stored in the pyquan or check_peak.ini file
Data is stored in the Peak_ID class, which can easily be accessed
to write down data in a data file.
The class Code, is the class where the actual quantification takes place,
plus the creation of a peak image.
The quantification algorithm can be found the the peak_fit.py module'''

import numpy as np
import baseline, peak_fit, peak_pars, sys


class Peak_ID(object):
    def __init__(self, sample, project, code, mass):
	self._project = project
	self._ID={}
	self._ID['sample'] = sample
	self._ID['code'] = code
        self._ID['mass'] = mass
	self._ID['real_area'] = None
        self._ID['real_x'] = None
        self._ID['real_y'] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    @property
    def ID(self):
        return self._ID

    @property
    def sample(self):
	return self._ID['sample']

    @property
    def code(self):
	return self._ID['code']

    @property
    def mass(self):
	return self._ID['mass']

    @mass.setter
    def mass(self, mass):
	self._ID['mass'] = mass
	return

    @property
    def fit(self):
	return self._ID['fit']

    @fit.setter
    def fit(self, fit):
	self._ID['fit'] = fit

    @property
    def RT(self):
	return self._ID['RT']

    @RT.setter
    def RT(self, RT):
        self._ID['RT'] = RT
	return

    @property
    def real_peak(self):
	return self._ID['real_peak']

    @real_peak.setter
    def real_peak(self, real_peak):
	self._ID['real_peak'] = real_peak
	return

    @property
    def param(self):
	return self._ID['param']

    @ param.setter
    def param(self, param):
	self._ID['param'] = param
	return

    @property
    def area(self):
	return self._ID['area']

    @area.setter
    def area(self, area):
	self._ID['area'] = area
	return


class Code():
    def __init__(self, ID, cdf, project):
        self._project = project
        self._ID = ID
        self._cdf = cdf
        self._window = project.info.peak_window
        
    def area(self, noise, fit_peak='yes'):
	'''fit peak, and store data in ID class'''
	pars = peak_pars.Pars(self._project.info)
	param_fit = {}
	param_fit['int'] = [None,None,None,None]
	time = []
	intensity = []
        self.get_data()
	try:
	    self.get_data()
	except:
	    return
        self._y = noise.correct(self._x,self._y)
        params, x_fit, y_fit = pars.get_param(self._x, self._y, self._ID.RT)
	if params:
	    fit = peak_fit.Fit(params, x_fit, y_fit)
	    if fit_peak == 'yes':
		self._ID.area, param_fit, fit_peak = fit.peak_fit()
		self._ID.RT = param_fit['int'][1]
	    if fit_peak != 'yes':
		self.real_area(pars)
		param_fit['int'] = [None,None,None,None]
	    self.save_image(param_fit, fit_peak=fit_peak)
	param_str = '{0} '.format(param_fit['int'][0])
	for i in range(1,4):
	    param_str += '{0} '.format(param_fit['int'][i])
	self._ID.param = param_str
	return

    def real_area(self, pars):
	self._x_real, self._y_real = pars.xy_int
        self._ID.area = np.trapz(self._y_real, self._x_real)
	start = self._cdf.time_index(self._x_real[0])
        end = self._cdf.time_index(self._x_real[-1])
	index = [start,end]
	real_x = ''
	real_y = ''
	for i in range(len(self._y_real)):
	   real_y += '{0} '.format(self._y_real[i])
	self._ID.real_peak = (index, real_y)
        return
    
    def get_data(self):
	time_len = len(self._cdf.scan_time) - 2
        t_idx = self._cdf.time_index(self._ID.RT)
	int_idx = None
        x = []
        y = []
        i = 0
	for t in range(t_idx-self._window, t_idx+self._window):
            if 0<=t< time_len:
                x.append(self._cdf.get_time(t))
                y.append(self._cdf.intensity(t,self._ID.mass))
		i+=1
		if t == t_idx:
		    int_idx = i
	if not int_idx:
	    return
	y -= baseline.baseline_poly(np.array(x),np.array(y), 
                                    window=self._window/2, deg=2)
        lim = self._window/2
	start = int_idx - lim
	if start < 0:#Defines left boundary (t=0)
	    start = 0
	end = int_idx + lim
	if end > time_len:
	    end = time_len
	self._x = x[start:end]
	self._y = y[start:end]
        return
        
    def save_image(self, pars, fit_peak = 'yes'):
        import matplotlib.pyplot as plt
        x = np.array(self._x)
        x_plot = x/60. #back to minutes
        y = np.array(self._y)
        plt.figure()
        plt.plot(x_plot,y)
        plt.xlabel('Time (min)')
        plt.ylabel('intensity')
        plot_name = self._project.path.pyquan_fig_file(self._ID.code, 
                                                       self._ID.sample)
        if fit_peak is 'yes':
            for i in pars:
                if pars[i][0]:
                    peak = peak_fit.Fit.asym_peak(x, pars[i])
                    if i == 'int':
                        plt.plot(x_plot, peak, 'r-')
                    else:
                        plt.plot(x_plot, peak, 'y-')
        else:
            plt.plot(self._x_real/60., self._y_real, 'r-')
        plt.savefig(plot_name)
        plt.close()
        return
