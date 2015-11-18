import numpy as np
import importdata as imp


'''Contains functions for (1) GC/MS data alignment, based on peak identifications.
   It returns images for each alignment, (2) project library, including automatic
   reference RT estimations, and (3) regression and median functions.'''

class SaveImage():
    def __init__(self, align_dir, sample_y):
        self._dir = align_dir
        self._sample_y = sample_y
        
    def save_image(self, x, y, sample_x, CF):
        import matplotlib.pyplot as plt
        import os.path
        x_line = np.arange(0.,max(x))
        y_line = x_line*CF[0]+CF[1]
        x = np.array(x)
        y = np.array(y)
        plt.figure()
        plt.scatter(x,y)
        plt.plot(x_line, y_line, 'r-')
        plt.xlabel(self._sample_y)
        plt.ylabel(sample_x)
        plot_name = os.path.join(self._dir,'{0}.png'.format(sample_x))
        plt.savefig(plot_name)
        plt.close()
        return

class AlignSample():
    def __init__(self, path, sample_y, RT_y):
        self._sample_y = sample_y
        self._RT_y = RT_y
        self._image = SaveImage(path.align_dir, sample_y)

    def align_sample(self, sample_x, RT_x):
        x=[]
        y=[]
        for code in self._RT_y:
            if code in RT_x:
                x.append(RT_x[code])
                y.append(self._RT_y[code])
        reg = Regression(x,y)
        CF = reg.lin_robust()
        self._image.save_image(x,y,sample_x,CF)
        return CF


class Library(object):
    '''Creates a project library. If automatic RT estimation is allowed, 
    reference RT value will be estimated from the AMDIS data, within the limits
    as written in the pyquan.ini file'''
    
    def __init__(self, path, info, RT_dict, CF_dict):
        self._path = path
        self._info = info
        self._CF = CF_dict
        self._library = imp.library_import(path.library_file_ref, self._info.csv)
        self._code_set = imp.get_codeset(RT_dict)
        if info.auto_RT == 'yes':
            self._cal_range = info.cal_range
            self._fit_min = info.min_fit
            self.get_median()
        
    def get_RT_new(self):
        self._RT_dict_new = {}
        self._fit_dict_new = {}
        for sample in self._path.runlist:
            ID = {}
            ID['sample'] = sample
            ID['CF'] = self._CF[sample]
            imp_sample = imp.Sample(ID, self._path, self._info.csv)
            self._RT_dict_new[sample], self._fit_dict_new[sample] = imp_sample.read_amdis()
        return
    
    def get_median(self):
        self.get_RT_new()
        self._code_count = {}
        for code in self._code_set:
            RT_list = []
            self._code_count[code] = 0
            for sample in self._path.runlist:
                if code in self._RT_dict_new[sample] and code in self._library:
                    self._code_count[code] += 1
                    RT = self._RT_dict_new[sample][code]
                    RT_ref = RT*self._CF[sample][0]+self._CF[sample][1]
                    if abs(RT_ref-self._library[code]['RT'])<self._cal_range:
                        RT_list.append(RT_ref)
            if RT_list:
                self._library[code]['RT'] = calc_median(RT_list)
        return
    
    def check_median(self):
        for code in self._code_set:
            RT_m = self._RT_median[code]
            if code in self._library:
                RT_r = self._library[code]['RT']
                if abs(RT_m - RT_r) < self._cal_range:
                    self._library[code]['RT'] = RT_m
        return
    
    def write_lib(self):
        with open(self._path.library_file, 'w') as lib:
            for code in sorted(self._code_set):
                if not code in self._library:
                    print '{0} not in reference library'.format(code)
                elif self._code_count[code] > self._fit_min:
                    i = self._library[code]
                    #i['lim'] = float(i['lim'])/5
                    line = '{0},{1},{2},{3},"{4}",{5}\n'.format(code,
                       i['RT'],i['lim'],i['mass'],i['name'],i['source'])
                    lib.write(line)
        return
  
    
class Regression(object):
    '''Function first tries to draw a line that connects most points, within a
    limited distance (0.01*max y). Next, a linear regression is applied through
    these lines.'''
    
    def __init__(self, x, y):
        self._x = x
        self._y = y
        
    def get_rc_list(self):
        self._rc_list=[]
        x_set = set()
        for i in range(len(self._x)):
            x_set.add(i)
            for j in range(len(self._x)):
                if not j in x_set and not self._x[i] == self._x[j]:
                    rc = (self._y[i]-self._y[j]) / (self._x[i] - self._x[j])
                    ic = self._y[i] - self._x[i]*rc
                    item = (i,j,rc,ic)
                    self._rc_list.append(item)
        return
        
    def get_line_list(self, item, lim):
        rc = item[2]
        ic = item[3]
        idx_list = []
        for i in range(len(self._x)):
            if abs(rc*self._x[i]+ic - self._y[i]) < lim:
                idx_list.append(i)
        return idx_list
    
    def lin_robust(self):
        lim = 0.01 #max distance from line, in fraction of max(y)
        lim = lim * max(self._y)
        self.get_rc_list()
        line_list = []
        for i in self._rc_list:
            idx_list = self.get_line_list(i, lim)
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
        [rc, ic] = np.polyfit(x_list, y_list, 1)
        return rc, ic
        

def calc_median(x):
    sorts = sorted(x)
    length =len(sorts)
    if length ==1:
        return x[0]
    elif not length % 2:
        return (sorts[length / 2] + sorts[length /2 -1]) /2.0
    else:
        return sorts[length /2]