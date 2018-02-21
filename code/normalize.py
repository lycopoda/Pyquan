import datafiles, mzratio, CDF, sys, normfiles, normfigures, baseline, peak_fit
import project as proj
import matplotlib.pyplot as plt

class WriteFiles(object):
    def __init__(self, project):
        self._makeline = project.csv.make_line
        self._RTfile = project.path.RT_file
        self._fitfile = project.path.fit_file
        self._areafile = project.path.area_norm_file
        self._codelist = []
        self._samplelist = []

    def write_RT(self, RTdict):
        for code in RTdict:
            for sample in RTdict[code]:
                try:
                    RTdict[code][sample] /= 60.
                except TypeError:
                    pass
        self.writedata('RT', RTdict, self._RTfile)
        return

    def write_fit(self, fitdict):
        self.writedata('fit', fitdict, self._fitfile)
        return

    def write_area(self, areadict):
        self.writedata('area_norm', areadict, self._areafile)
        return

    def writedata(self, item, datadict, filename):
        with open(filename, 'w') as f:
            f.write(self.header(item))
            for code in self._codelist:
                datalist = [code]
                for sample in self._samplelist:
                    datalist.append(datadict[code].get(sample, 'ND'))
                f.write(self._makeline(datalist))
        return

    def header(self, item):
        headerlist = [item] + self._samplelist
        return self._makeline(headerlist)


class MakeFigures(object):
    def __init__(self, normalize, sample):
        self._CF = normalize.CF
        self._project = normalize._project
        self._sample = sample
        self._cdf = CDF.CDF(sample)
        self._baseline = baseline.baseline_poly(self._cdf.scan_time,
                         self._cdf.total_TIC, window=50, deg=10)
        self.get_peaks()

    def make_figures(self):
        step = 10.
        lim = {}
        lim['complete'] = [0,1]
        for i in range(1,int(step)+1):
            lim[i] = []
            lim[i].append(i/step -1/step)
            lim[i].append(i/step)
        self.save_image(lim)

    def save_image(self, lim):
        time = self._cdf.scan_time / 60.
        x_max = max(time)
        l_time = len(time)
        for i in lim:
            name = self._project.path.norm_fig_file(self._sample,str(i))
            start = int(lim[i][0] * l_time)
            end = int(lim[i][1] * l_time)
            time_lim = time[start:end]
            total_lim = self._cdf.total_TIC[start:end]
            baseline_lim = self._baseline[start:end]
            peak_lim = self._peakTIC[start:end] + baseline_lim
            self.create_image(time_lim, total_lim, baseline_lim, peak_lim,
            name)
        return

    def get_peaks(self):
        print('\r\tget peaks {0}\t\t'.format(self._sample),)
        sys.stdout.flush()
        self._peakTIC = self._cdf.empty_TIC
        with datafiles.HDF5(self._project.path.hdf5) as f:
            peakparam = f.getparam(sample=self._sample)
        for code in peakparam:
            CF = self._CF(code)
            try:
                self._peakTIC += peak_fit.Fit.asym_peak(self._cdf.scan_time,
                        peakparam[code]['param']) * CF
            except KeyError:
                try:
                    xs = peakparam[code]['real_x']
                    y = peakparam[code]['real_y'] * CF
                    for i in range(xs[0],xs[1]):
                        self._peakTIC[i] += y[i]
                except KeyError:
                    print('no peak data of {0}'.format(code))
                    pass
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


class Normalize(object):
    def __init__(self, project):
        print('Normalize peaks')
        sys.stdout.flush()
        self._project = project
        self.getmzratio()

    def getmzratio(self):
        self._CF = {}
        CF = mzratio.CF(self._project)
        for code in self._project.lib.library:
            self._CF[code] = CF.CF(code)
        return

    def CF(self, code):
        return self._CF[code]

    def writedata(self):
        print('Write output files')
        sys.stdout.flush()
        writefiles = WriteFiles(self._project)
        with datafiles.HDF5(self._project.path.hdf5) as f:
            f.get_project_data()
            writefiles._samplelist = f.samplelist
            writefiles._codelist = f.codelist
            writefiles.write_RT(f.RTdict)
            writefiles.write_fit(f.fitdict)
            self._areadict = f.areadict
        self.normalize()
        writefiles.write_area(self._areadict)
        return

    def normalize(self):
        norm = self._project.info.norm_method
        sampleset = set()
        for code in self._areadict:
            for sample in self._areadict[code]:
                sampleset.add(sample)
        if not [sample for sample in self._project.runlist if 
                        sample in  sampleset]:
            print('ERROR: Sample {0} '.format(sample) +
                    'not in results, uncheck sample from' +
                    'runlist, or rerun quantify.') 
            sys.exit(2)
        for code in self._areadict:
            CF = self._CF[code]
            for sample in self._areadict[code]:
                try:
                    self._areadict[code][sample] *= CF
                except TypeError:
                    pass
        if norm == 'tic':
            print('Normalization against TIC')
            self.norm_tic()
        elif norm == 'sum':
            print('Normalization against sum')
            self.norm_sum()
        elif norm:
            print('Normalization against {0}'.format(norm))
            code = amdis.correct_code(norm)
            if code in self._project.library:
                self.norm_std(code)
            else:
                print('ERROR: code for internal standard not present')
                print('Change norm_method in pyquan.ini')
                sys.exit(2) 
        if self._CFnorm:
            for code in  self._areadict:
                for sample in self._CFnorm:
                    try:
                        self._areadict[code][sample] /=self._CFnorm[sample]
                    except TypeError:
                        pass
        return

    def norm_std(self, code):
        self._CFnorm = {}
        for samples in self._project.runlist:
            try:
                self._CFnorm[sample] = self._areadict[sample][code]
            except KeyError:
                print('ERROR: Internal standard not present in all samples')
                print('Choose different standard or method in pyquan.ini')
                sys.exit(2)
        return
    
    def norm_sum(self):
        self._CFnorm = dict.fromkeys(self._project.runlist, 0.)
        for code in self._areadict:
            for sample in self._CFnorm:
                try:
                    self._CFnorm[sample] += self._areadict[code][sample]
                except TypeError:
                    pass
        return

    def norm_tic(self):
        self._CFnorm = {}
        for sample in self._project.runlist:
            self._CFnorm[sample] = sum(self._TIC[sample]) - \
                                   sum(self._baseline[sample])
        return            


def main(project_name=None):
    if not project_name:
        import analyse
        project_name = analyse.get_project_name()
    project = proj.Project(project_name)
    project.read_library()
    normalize = Normalize(project)
    normalize.writedata()
    for sample in project.runlist:
        MakeFigures(normalize, sample).make_figures()
    return 0 

if __name__=='__main__':
    status = main()
    sys.exit(status)    
