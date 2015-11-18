'''This module order pyquan datasets from individual samples into
overview matrixes of RT, RT_ref, fit, area and normalized area.
Additionally, overlay images can be made of total TIC, baseline and quantified
peaks.'''


import baseline, sys, init, os, peak_fit, pyquan
import importdata as imp
import matplotlib.pyplot as plt
import numpy as np

#Reverses key levels in dictionary
def rev(data_dict):
    rev_dict = {}
    for x in data_dict:
        for y in data_dict[x]:
            if not y in rev_dict:
  	        rev_dict[y] = {}
    for y in rev_dict:
	for x in data_dict:
	    if y in data_dict[x]:
                rev_dict[y][x] = data_dict[x][y]
    return rev_dict

#----------------------------------------------------------------------------

class Library(object):
    def __init__(self, info, path):
	self._info = info
	self._path = path
	self.import_cf()

    def import_cf(self):
	import massratio
        self._code_missing = set()
        lib_amdis = self._path.library_amdis
        min_mass, max_mass = self._info.mass_limits
        lib_project = self._path.library_file
        self._CF = massratio.Library(lib_amdis, min_mass,
			max_mass, lib_project, self._info.csv)
        return
    
    def code_cf(self,code):
        CF = self._CF.CF(code)
        return CF


#-------------------------------------------------------------------------------

class TIC_Sample(object):
    def __init__(self, sample, project, library):
        self._sample =  pyquan.Sample(project, sample)
	self._cdf = imp.CDF(sample)
	self._library = library
	self._path = project.path
	self._total_TIC = None
	self._baseline = None
	self._time = None

    def scan_time(self):
    	self._time = self._cdf.scan_time
        return

#create images
    def save_images(self):
	if not self._time:
	    self.baseline()
	self.calc_peak_TIC()
        step = 10.
        lim = {}
        lim['complete']=[0,1]
        for i in range(1,int(step)+1):
            lim[i] = []
            lim[i].append(i/step-1/step)
            lim[i].append(i/step)
        self.save_image(lim)
        return

    def real_peak(self,index,intensity, cf):
	start, end = index.split(" ")
	start = int(start)
	end = int(end)
	intensity = intensity.split(" ")
	y = self._cdf.empty_TIC
	if cf == None:
	   return y
	for i in range(start,end):
	    y[i] = float(intensity[(i-start)])*cf
	return y

    def calc_peak_TIC(self):
	self._peak_TIC = self._cdf.empty_TIC
        with open(self._sample.datafile, 'r') as data_file:
	    data_file.readline()
	    for line in data_file:
                info = line.strip().split(',')
		param = info[4].split(" ")[:4]
		cf = self._library.code_cf(info[0])
		if param[1] != 'None':
		    peak = peak_fit.Fit.asym_peak(self._time, param) * cf
		else:
		    peak = self.real_peak(info[5],info[6], cf)
		self._peak_TIC += peak
        return

    def save_image(self, lim):
        time = self._time/60.
	x_max = max(time)
	for i in lim:
	    name = self.plotname(self._sample.sample,str(i))
            start = int(lim[i][0]*len(time))
	    end = int(lim[i][1]*len(time))
            time_lim = time[start:end]
	    total_lim = self._total_TIC[start:end]
	    peak_lim = self._peak_TIC[start:end] + self._baseline[start:end]
	    baseline_lim = self._baseline[start:end]
	    self.create_image(time_lim, total_lim, peak_lim, baseline_lim, name)
	return

    def plotname(self, sample, part):
        return self._path.norm_fig_file(sample, part)

    def create_image(self, time, total, peak, baseline, name):
        plt.figure()
	plt.plot(time, total, 'k-')
	plt.plot(time, peak, 'r-')
	plt.plot(time, baseline, 'b-')
	plt.xlabel('time (min)')
	plt.ylabel('TIC')
	plt.savefig(name)
	plt.close()
	return

    def baseline(self):
    	self._time = self._cdf.scan_time
	self._total_TIC = self._cdf.total_TIC
	self._baseline = baseline.baseline_poly(self._time,
			self._total_TIC, window=50, deg=10)
	return

    @property
    def norm_TIC(self):
	self.baseline()
	return sum(self._total_TIC) - sum(self._baseline)


#-------------------------------------------------------------------------------        

#-------------------------------------------------------------------------------
	
'''
Class to write overview data files, normalize peak areas,
and create TIC overview graphs.
'''
class Write_data(object):
    def __init__(self, project):
	self._project = project
	self._codelist = []
	self._lib = Library(project.info, project.path)

    @property
    def missing_codes(self):
        return self._code_missing

    def data_dict(self, index):
	sep = self._project.csv.sep
	data_dict = {}
	for item in self._project.runlist:
	    sample = pyquan.Sample(self._project, item)
	    sample_dict = {}
	    with open(sample.datafile, 'r') as data_file:
		data_file.readline()
		for line in data_file:
		    info = line.strip().split(sep)
		    sample_dict[info[0]] = info[index]
            for code in self._codelist:
		try:
		    data_point = sample_dict[code]
		except KeyError:
		    data_point = 'ND'
	        data_dict.setdefault(code,[]).append(data_point)
	return data_dict

    def area_dict(self):
	data_dict = self.data_dict(index=1)
	self._code_missing = set()
	for code in data_dict:
	    CF = self._lib.code_cf(code)
	    if CF == 'key' or CF == 'AMDIS':
		self._codes_missing.add(code, CF)
            else:
		for i in range(len(self._project.runlist)):
		    try:
		        area = float(data_dict[code][i])*CF
		    except:
			area = 0.
	            data_dict[code][i] = area
	return data_dict

    def shape_dict(self, data_dict):
	data_new = {}
	for code in self._codelist:
	    for sample in self._project.runlist:
	        data_new

    def RT_ref_dict(self):
        from operator import itemgetter
	sep = self._project.csv.sep
	RT_ref_dict = {}
	RT_code_dict = {}
	for item in self._project.runlist:
	    sample = pyquan.Sample(self._project, item)
	    CF = self._project.CF(item)
	    with open(sample.datafile, 'r') as data_file:
		data_file.readline()
		for line in data_file:
		    info = line.strip().split(sep)
		    try:
			RT_ref = float(info[2])*CF[0]+CF[1]
			RT_code_dict.setdefault(info[0],[]).append(RT_ref)
		    except:
			RT_ref = 'ND'
	RT_mean_dict = {}
        for code in RT_code_dict:
	    RT_mean_dict[code] = sum(RT_code_dict[code])/len(RT_code_dict[code])
	for code in sorted(RT_code_dict.iteritems(), key=itemgetter(1)):
	    self._codelist.append(code[0])
	return RT_code_dict
	
    def write_header(self):
        sep = self._project.csv.sep
        self._header = 'code{0}'.format(sep)
	for sample in self._project.runlist:
	    self._header += '{0}{1}'.format(sample, sep)
	self._header += '\n'
	return

    def write_file(self, data_file, data_dict):
        sep = self._project.csv.sep
        with open(data_file, 'w') as data_file:
	    data_file.write(self._header)
	    for code in self._codelist:
	        line = '{0}{1}'.format(code, sep)
		for item in data_dict[code]:
		    line += '{0}{1}'.format(item,sep)
		line += '\n'
	        data_file.write(line)
	return

    def norm_factor(self, sample, local_dict, method=None):
	tic = TIC_Sample(sample, self._project, self._lib)
        if method == 'sum':
	    norm = 0.
	    for code in local_dict:
		try:
		    norm += float(local_dict[code])
		except:
		    pass
	elif method == 'TIC':
	    #calculate total TIC minus baseline
	    norm = tic.norm_TIC
        elif method:
	    std = method   
	    try:
	        norm = float(local_dict[std])
	    except KeyError:
		print 'Internal standard not present in {0}'.format(sample)
		print 'Choose other standard or change method, an rerun normalization.py.'
		sys.exit(2)
	else:
	    norm = 1.
	return norm, tic

    def check_method(self):
	method = self._project.info.norm_method
	answer = ['sum','tic']
	if method not in answer:
	    std = imp.correct_code(method)
	    try:
                self._library.code_cf(std)
		method = std
	    except KeyError:
                print 'Normalization method {0} is not recognized as compound code\nor normalization method'.format(std)
		print 'Normalization step skipped.'
		method = None
	return method
     
    def normalize(self, area_dict):
	method = self.check_method()
	image = self._project.info.TIC_images
	runlist = self._project.runlist
	for i in range(len(runlist)):
	    print '{0}\tNormalize area\t'.format(runlist[i]),
	    local_area = {}
	    for code in area_dict:
	        local_area[code] = area_dict[code][i]
	    norm, tic = self.norm_factor(runlist[i], local_area, method=method)
            for code in self._codelist:
		try:
		    area_dict[code][i] = float(local_area[code])/norm
		except KeyError:
		    pass
	    if image == 'yes':
		print 'Create TIC images\t',
		tic.save_images()
	    print 'Finished.'
	self.write_file(self._project.path.area_norm_file, area_dict)
	return

    def write_data(self):
	RT_ref_dict = self.RT_ref_dict()
	if not self._codelist:
	    print 'No quantified compounds.'
	    sys.exit(2)
	self.write_header()
	p = self._project.path
	self.write_file(p.RT_ref_file, RT_ref_dict)
	self.write_file(p.fit_file, self.data_dict(index=3))
	area_dict = self.area_dict()
	self.write_file(p.area_file, area_dict)
	self.normalize(area_dict)
	return

#--------------------------------------------------------------------------

def create_dir(path):
    if not os.path.exists(path.norm_dir):
        os.mkdir(path.norm_dir)
    return

def main(project_name = None):
    if not project_name:
        import analyse
        project_name = analyse.get_project_name()
    print '{0}: start normalization.'.format(project_name)
    project = pyquan.Project(project_name, init_file='pyquan.ini')
    project.pyquan()
    create_dir(project.path)
    write_data = Write_data(project)
    print 'Write data files.'
    write_data.write_data()
    if write_data.missing_codes:
	print 'The followings compounds are either missing from the AMDIS library,'
	print 'or mass not present in mass spectrum:'
	for code in sorted(write_data.missing_codes):
	    print code
    print('\a')
    return


if __name__=='__main__':
    status = main()
    sys.exit(status)
 
 
