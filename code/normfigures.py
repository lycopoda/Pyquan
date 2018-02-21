import peak_fit, sys
import matplotlib.pyplot as plt

class NormFigures(object):
    def __init__(self, normalize, sample, hdf5):
        self._norm = normalize
        self._f = hdf5
        self._sample = sample
        self.getCDFdata()

    def getCDFdata(self):
        
        self._time = data._time[sample]
        self._baseline = data._baseline[sample]
        self._totalTIC = data._TIC[sample]
        self._datadict = data._datadict
        self._emptyTIC = data._emptyTIC[sample]
        self.getpeaks()

    def make_figures(self):
        step = 10.
        lim = {}
        lim['complete'] = [0,1]
        for i in range(1,int(step)+1):
            lim[i] = []
            lim[i].append(i/step-1/step)
            lim[i].append(i/step)
        self.save_image(lim)

    def save_image(self, lim):
        x_max = max(self._time)
        l_time = len(self._time)
        for i in lim:
            name = self._project.path.norm_fig_file(self._sample,str(i))
            start = int(lim[i][0] * l_time)
            end = int(lim[i][1] * l_time)
            time_lim = self._time[start:end]
            total_lim = self._totalTIC[start:end]
            baseline_lim = self._baseline[start:end]
            peak_lim = self._peakTIC[start:end] + baseline_lim
            self.create_image(time_lim, total_lim, baseline_lim, peak_lim, name)
            print(self._peakTIC[start:end])
            sys.exit(2)
        return

    def create_image(self, time, total, baseline, peak, name):
        plt.figure()
        plt.plot(time, total, 'k-')
        plt.plot(time, peak, 'r-')
        plt.plot(time, baseline, 'b-')
        plt.xlabel('time (min)')
        plt.ylabel('TIC')
        plt.savefig(name)
        plt.close()
        return

    def getpeaks(self):
        print('\r\tget peaks {0}\t\t'.format(self._sample),)
        sys.stdout.flush()
        self._peakTIC = self._emptyTIC
        for code in self._data._datadict[self._sample]:
            ID = self._datadict[self._sample][code]
            print(ID['param'])
            sys.exit(2)
            if ID['param']:
                self._peakTIC += peak_fit.Fit.asym_peak\
                                 (self._time, ID['param']) 
            elif 'real_x' in ID:
                for i in range(ID['real_x'][0],ID['real_x'][1]):
                    self._peakTIC[i] += ID['real_y'][i]
        return
