import numpy as np

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
