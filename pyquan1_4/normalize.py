import datafiles, mzratio, CDF, sys, normfiles, normfigures, baseline
import project as proj

class Data(object):
    def __init__(self, project, normalize):
        project.read_library()
        self._project = project
        self._normalize = normalize
        self.import_data()

    def import_data(self):
        self.cdf()
        self._datadict = {}
        for sample in self._project.runlist:
            data = datafiles.DataFiles(self._project, sample).read_file()
            self._datadict[sample] = data
        self.get_area_TIC()
        self.norm_area()
        return

    def cdf(self):
        self._baseline = {}
        self._TIC = {}
        self._time = {}
        self._emptyTIC = {}
        for sample in self._project.runlist:
            cdf = CDF.CDF(sample)
            self._emptyTIC[sample] = cdf.empty_TIC
            self._time[sample] = cdf.scan_time
            self._TIC[sample] = cdf.total_TIC
            self._baseline[sample] = baseline.baseline_poly\
                                     (self._time[sample], self._TIC[sample],
                                      window=50, deg=10)
        return

    def get_area_TIC(self):
        for code in self._project._library._lib:
            CF = self._normalize.CF(code)
            for sample in self._project.runlist:
                try:
                    self._datadict[sample][code]['area'] *= CF
                except KeyError:
                    pass
                try:
                    self._datadict[sample][code]['param'][0] *= CF
                except KeyError:
                    pass
                except IndexError:
                    pass 
                try:
                    self._datadict[sample][code]['real_area'] *= CF    
                except KeyError:
                    pass
        return

    def norm_area(self):
        norm = self._project.info.norm_method
        if norm == 'tic':
            print 'Normalization against TIC'
            sys.stdout.flush()
            self.norm_tic()
        elif norm == 'sum':
            print 'Normalization against sum'
            sys.stdout.flush()
            self.norm_sum()
        elif norm:
            print 'Normalization against {0}'.format(norm)
            sys.stdout.flush()
            code = amdis.correct_code(norm)
            if code in self._project.library:
                self.norm_std(code)
            else:
                print 'ERROR: code for internal standard not present'
                print 'Change norm_method in pyquan.ini'
                sys.exit(2) 
        if self._CFnorm:
            for sample in  self._project.runlist:
                for code in self._datadict[sample]:
                    self._datadict[sample][code]['area_norm'] =\
                    self._datadict[sample][code]['area'] / self._CFnorm[sample] 
        return

    def norm_std(self, code):
        self._CFnorm = {}
        for samples in self._project.runlist:
            try:
                self._CFnorm[sample] = self._datadict[sample][code]['area']
            except KeyError:
                print 'ERROR: Internal standard not present in all samples'
                print 'Choose different standard or method in pyquan.ini'
                sys.exit(2)
        return
    
    def norm_sum(self):
        self._CFnorm = {}
        for sample in self._project.runlist:
            area = 0.
            for code in self._datadict[sample]:
                area += self._datadict[sample][code]['area']
            self._CFnorm[sample] = area
        return

    def norm_tic(self):
        self._CFnorm = {}
        for sample in self._project.runlist:
            self._CFnorm[sample] = sum(self._TIC[sample]) - \
                                   sum(self._baseline[sample])
        return            


class Normalize(object):
    def __init__(self, project):
        print 'Collect data'
        sys.stdout.flush()
        self._project = project
        self._codelist = []
        self._mzratio = mzratio.CF(project)
        self._data = Data(project, self)
        print 'Write output files'
        sys.stdout.flush()
        self._normfiles = normfiles.NormFiles(project, self)
        self._normfiles.writefiles()

    def CF(self, code):
        return self._mzratio.CF(code)

    def writedata(self):
        files = normfiles.NormFiles(self._project, self)
        files.writefiles()
        return

    def makefigures(self):
        print 'Create output figures'
        sys.stdout.flush()
        for sample in self._project.runlist:
            figures = normfigures.NormFigures(self._project, sample, self._data)
            figures.make_figures()
        print '\nFinished'
        return

def main(project_name=None):
    if not project_name:
        import analyse
        project_name = analyse.get_project_name()
    project = proj.Project(project_name)
    project.read_library()
    normalize = Normalize(project)
    normalize.writedata()
    normalize.makefigures()
    return 0 

if __name__=='__main__':
    status = main()
    sys.exit(status)    
