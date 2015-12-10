import sys, init, peak, pyquan
import importdata as imp
import peak_pars as pars
import noise_reduction as noise


class Sample(object):
    def __init__(self, ID, project, csv):
        self._project = project
        self._ID = ID
        self._cdf = imp.CDF(ID['sample'])
        self._imp = imp.Sample(ID['sample'], project._path, csv, CF=ID['CF'])

    @property
    def scan_time(self):
	return self._cdf.scan_time

    @property
    def cdf(self):
	return self._cdf
        
    def read_data(self):
        self._imp.read_amdis()
        self._imp.backfill()
        self._cdf.import_data()
        return
        
    def update_ID(self, code):
	import decimal
        self._ID['code'] = code
	try:
            RT = self._imp.RT_dict[code]
	except:
	    print 'code not in library'
	    sys.exit(2)
        if not self._ID['RT']:
            self._ID['RT'] = RT
	self._ID['fit'] = self._imp.fit_dict[code]
        self._ID['mass'] = self._project._library[code]['mass']
	print '{0}\t{1}{2}\tRT: {3}\tRT_ref: {4}'.format(self._ID['sample'],self._ID['code'],
                                                         self._ID['mass'],
							 round(self._ID['RT']/60.,2),
			        round(self._ID['RT']*self._ID['CF'][0]+self._ID['CF'][1],2))
        return
    

def update_datafile(project, ID):
        with open(project.path.datafile(ID.sample), 'r') as old:
            data_old = old.readlines()
        with open(project.path.datafile(ID.sample), 'w') as datafile:
            for line in data_old:
                code = line.split(',')[0]
                if code != ID.code:
                    datafile.write(line)
            datafile.write(ID.dataline)
        return

def main():
    info = init.Info('check_peak.ini')
    csv = init.Info('pyquan.ini').csv
    RT = info.RT_check
    project_name = info.project_name_check
    print project_name
    path = init.Path(project_name, info)
    project = pyquan.Project(project_name, init_file='check_peak.ini')
    project.pyquan()
    sample_check = info.sample_check
    if sample_check == 'all':
        samplelist = project.runlist
    elif sample_check in project.runlist:
	samplelist = [sample_check]
    else:
	print '{0} not in sample list, check check_peak.ini file'.format(sample_check)
	sys.exit(2)
    for sample in samplelist:
	print sample,
	sample_class = pyquan.Sample(project, sample)
	sample_class.read_data()
	ID =  pyquan.get_ID(project, sample_class, info.code_check)
	if info.RT_check:
	    ID.RT = float(info.RT_check)
        peak_fit = peak.Code(ID, sample_class, project)
        status = peak_fit.area(noise=noise.NoiseReduction(info), fit_peak = info.fit_peak)
	if status == 2:
	    print 'data collection failed'
	elif ID.area:
	    print '\tRT={0}'.format(float(ID.RT)/60.) 
	    update_datafile(project, ID)
	else:
	    print 'Peak fit not succeeded, change fit parameters'
    print('\a')

if __name__=='__main__':
    status = main()
    sys.exit(status)
