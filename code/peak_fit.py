import numpy as np

class Fit(object):
    '''Deconvolute peaks, and quantify peak of interest'''
    
    def __init__(self, params, x_fit, y_fit):
        self._pars = params
        self._x_fit = x_fit
        self._y_fit = y_fit
        return
                
    def peak_fit(self):
        from scipy.optimize import curve_fit
        area = None
        param = self._pars['left'] + self._pars['int'] + self._pars['right']
        indexes = [9,5,1]
        for index in indexes:
            del param[index]
        if self._pars['int'][0]:
            try:
                if self._pars['left'][0] and self._pars['right'][0]:
                    popt, pcov = curve_fit(self.peak_int_right_left1,
                                           self._x_fit, self._y_fit, param)
                    param2 = np.insert(popt, [1,4,7], [self._pars['left'][1],
                                  self._pars['int'][1], self._pars['right'][1]])
                    popt, pcov = curve_fit(self.peak_int_right_left2,
                                           self._x_fit, self._y_fit, param2)
                    self._pars['left'] = popt[:4]
                    self._pars['int'] = popt[4:8]
                    self._pars['right'] = popt[8:]
                elif self._pars['left'][0]:
                    param = param[:6]
                    popt, pcov = curve_fit(self.peak_int_left1, self._x_fit,
                                           self._y_fit, param)
                    param2 = np.insert(popt, [1,4], [self._pars['left'][1],
                                       self._pars['int'][1]])
                    popt, pcov = curve_fit(self.peak_int_left2, self._x_fit,
                                           self._y_fit, param2)
                    self._pars['left'] = popt[:4]
                    self._pars['int'] = popt[4:]
                elif self._pars['right'][0]:
                    param = param[3:]
                    popt, pcov = curve_fit(self.peak_int_right1, self._x_fit,
                                           self._y_fit, param)
                    param2 = np.insert(popt, [1,4], [self._pars['int'][1],
                                       self._pars['right'][1]])
                    popt, pcov = curve_fit(self.peak_int_right2, self._x_fit,
                                           self._y_fit, param2)
                    self._pars['int'] = popt[:4]
                    self._pars['right'] = popt[4:]
                else:
                    param = param[3:6]
                    popt, pcov = curve_fit(self.peak_int1, self._x_fit,
                                           self._y_fit, param)
                    param2 = np.insert(popt, 1, self._pars['int'][1])
                    popt,pcov = curve_fit(self.peak_int2, self._x_fit,
                                          self._y_fit, param2)
                    self._pars['int'] = popt        
#numerical solution to estimate area of EGH, see Lan and Jorgenson, 2001
                t = np.arctan(abs(self._pars['int'][3])/\
                              abs(self._pars['int'][2]))
                p=[4., 6.293724, 9.232834, 11.342910, 9.123978, 
                   4.173753, 0.827797]
                epsilon = p[0]-p[1]*t+p[2]*t**2-p[3]*t**3+p[4]*t**4-\
                          p[5]*t**5+p[6]*t**6
                area = abs(self._pars['int'][0])*(self._pars['int'][2]*\
                       np.sqrt(np.pi/8)+abs(self._pars['int'][3]))*epsilon
                fit = 'yes'
            except:
                area = None
                fit = 'no'
        return area, self._pars, fit
   
    @staticmethod
    def asym_peak(t, pars_it):# EGH function, see Lan and Jorgenson, 2001, J. Chromatography 915: 1-13
        a0 = abs(float(pars_it[0])) #height
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
        if a11>a21:
            p_int = p_int*10e+12
            p_left = p_left*10e+12
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
        if a21 > a31:
            p_int = p_int*10e+12
            p_right = p_right*10e+12
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
        if a31<a21 or a21<a11:
            p_int = p_int*10e12
            p_right = p_right*10e12
            p_left = p_left*10e12
        return p_int+p_right+p_left
        
