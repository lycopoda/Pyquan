'''
Project class collects project level info (runlist, library,
quantification parameters)
Sample class collects sample level info (peak list, cdf data).
Actual quantification is done in peak.py module.
Data is stored in a data file, defined in peak.py
'''

import sys, init, peak, os
import importdata as imp
import peak_pars as pars
import noise_reduction as noise


class Project(object):
    def __init__(self, project_name, init_file='pyquan.ini'):
	self._project_name = project_name
        self._info = init.Info(init_file)
        self._path = init.Path(project_name, self._info)
	self._csv = self._info.csv
	self._CFdict = {}

    @property
    def project_name(self):
	return self._project_name

    @property
    def path(self):
	return self._path

    @property
    def info(self):
	return self._info

    @property
    def fit_peak(self):
	return self._fit_peak

    @property
    def noise(self):
	return self._noise

    def mass(self, code):
	return self._library[code]['mass']

    @property
    def info(self):
        return self._info

    def pyquan(self):
	self.get_CF_dict()
        self.create_dir()
        self._library = imp.library_import(self._path.library_file,
			self._info.csv)
        self._param = pars.Pars(self._info)
        self._noise = noise.NoiseReduction(self._info)
	self._fit_peak = self._info.fit_peak

    def create_dir(self):
        if not os.path.exists(self._path.data_dir):
            os.mkdir(self._path.data_dir)
        if not os.path.exists(self._path.images_dir):
            os.mkdir(self._path.images_dir)
        return
    
    def get_CF_dict(self):
        with open(self._path.runlist_file, 'r') as runlistfile:
            for line in runlistfile:
                sample, rc, ic = line.strip().split(',')
                self._CFdict[sample.lower()] = (float(rc), float(ic))
        return 

    @property
    def runlist(self):
	return self._path.runlist

    def CF(self, sample):
	if not self._CFdict:
            self.get_CF_dict()
	return self._CFdict[sample]

    @property
    def csv(self):
	return self._csv



class Sample(object):
    def __init__(self, project, sample):
        self._project = project
        self._sample = sample
	self._datafile = project._path.datafile(sample)
        self._cdf = imp.CDF(sample)
        self._imp = imp.Sample(sample, project.path, project.info.csv, CF=project.CF(sample), cal=0)

    @property
    def codeset(self):
	return self._codeset

    @property
    def datafile(self):
	return self._datafile

    def RT(self, code):
	return self._imp.RT_code(code)

    def fit(self, code):
	return self._imp.fit_code(code)
        
    def read_data(self):
        self._imp.read_amdis()
        self._imp.backfill()
	self._codeset = self._imp.codeset
        self._cdf.import_data()
        return

    def write_header(self):
        header_list = ['area', 'RT', 'fit', 'param', 'real_x', 'real_y']
        header = 'code{0}'.format(self._project.csv.sep)
        for item in header_list:
	    header += '{0}{1}'.format(item, self._project.csv.sep)
        header += '\n'	
        with open(self._project.path.datafile(self._sample), 'w') as data_file:
	    data_file.write(header)
        return

    @property
    def scan_time(self):
        return self._cdf.scan_time

    @property
    def sample(self):
	return self._sample

    def time_index(self, RT):
	return self._cdf.time_index(RT)

    def get_time(self, t):
	return self._cdf.get_time(t)

    def intensity(self, t, mass):
	return self._cdf.intensity(t, mass)

    def close_cdf(self):
	self._cdf.close_cdf()
	return


def get_ID(project, sample, code):
    ID = peak.Peak_ID(sample.sample, project, code)
    ID.RT = sample.RT(code)
    ID.fit = sample.fit(code)
    ID.mass = project.mass(code)
    return ID

def quantify_peaks(project, sample):
    sample.read_data()
    with open(project.path.datafile(sample.sample), 'a') as datafile:
	print '{0}: quantification'.format(sample.sample),
	for code in sorted(sample.codeset):
	    print '\r{0}: quantification {1}\t\t'.format(sample.sample, code),
	    ID = get_ID(project, sample, code)
	    peak_fit = peak.Code(ID, sample, project)
	    peak_fit.area(noise=project.noise, fit_peak=project.fit_peak)
	    try:
		datafile.write(ID.dataline)
	    except:
		pass
        print '\r{0}: quantification finished\t\t'.format(sample.sample)
	sample.close_cdf()
    return

def main(project_name = None):
    if not project_name:
        import analyse
        project_name = analyse.get_project_name()
    datarun = Project(project_name)
    if not project_name:
        project_name = sys.argv[1]
    project = Project(project_name)
    project.pyquan()
    for sample in project.runlist:
        samplerun = Sample(project, sample)
	samplerun.write_header()
        quantify_peaks(project, samplerun)
    print('\a')


if __name__=='__main__':
    status = main()
    sys.exit(status)
