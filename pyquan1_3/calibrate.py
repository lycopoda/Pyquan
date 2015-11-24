import pyquan, os, sys, collections
import statistics as stat
import importdata as imp
import numpy as np


class SaveImage():
    def __init__(self, align_dir, sample_y):
        self._dir = align_dir
        self._sample_y = sample_y
        
    def save_image(self, x, y, CF, sample_x):
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

#---End of Class SaveImage-------------------------------------------

class Library(object):
    '''Creates a project library. If automatic RT estimation is allowed, 
    reference RT value will be estimated from the AMDIS data, within the limits
    as written in the pyquan.ini file'''
    
    def __init__(self, project, RT_dict, CF_dict):
        self._path = project.path
        self._info = project.info
        self._CF = CF_dict
        self._library = imp.library_import(self._path.library_file_ref, self._info.csv)
        self._code_set = imp.get_codeset(RT_dict)
        if self._info.auto_RT == 'yes':
            self._cal_range = self._info.cal_range
            self._fit_min = self._info.min_fit
            self.get_median()
        
    def get_RT_new(self):
        self._RT_dict_new = {}
        self._fit_dict_new = {}
        for sample in self._path.runlist:
            imp_sample = imp.Sample(sample, self._path, self._info.csv, cal=1, CF=self._CF[sample])
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
                self._library[code]['RT'] = stat.calc_median(RT_list)
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
        code_list = []
	make_line =self._info.csv.make_line
        for code in self._code_set:
            if not code in self._library:
                print '{0} not in reference library'.format(code)
            elif self._code_count[code] > self._fit_min:
		RT = self._library[code]['RT']
                code_list.append((code, RT))
	code_list = sorted(code_list, key=lambda x: x[1])
	code_list = [i[0] for i in code_list]
        with open(self._path.library_file, 'w') as lib:
	    lib.write(make_line(["Code","RT","Limit","Mass","Name","Source"]))
	    for code in code_list:
	        i = self._library[code]
		info =[code,i['RT'],i['lim']/5,"+".join(i['mass']),i['name'],i['source']]
		lib.write(make_line(info))
#               i['lim'] = float(i['lim'])/5
#		mass = "+".join(i['mass'])
#		line =make_line([code,i['RT'],i['lim'],mass,i['name'],i['source']])
#                lib.write(line)
        return
  
#---End of Class Library----------------------------------------------

class Align(object):
    def __init__(self, project, RT_dict, runlist):
	self._slope = project.info.slope
	self._path = project.path
	self._info = project.info
	self._ref = project.info.sample_ref-1
	self._runlist = runlist
	self._RT = RT_dict

    def align(self):
	CF = {}
	self._ref_name = self._runlist[self._ref]
	CF[self._ref_name] = (1.,0.)
	for sample in self._runlist:
            if not sample == self._ref_name:
	        print '\rAlign {0}\t\t'.format(sample),
		CF[sample] = self.align_sample(sample)
	print '\rAlign samples finished'
 	print 'Align against reference library.'
        CF = self.align_ref(CF)
	print '\rAlign samples finished'
	return CF

    def align_sample(self, sample):
	image = SaveImage(self._path.align_dir,sample_y=self._runlist[self._ref])
	x=[]
	y=[]
	for code in self._RT[self._ref_name]:
	    if code in self._RT[sample]: 
		x.append(self._RT[sample][code])
		y.append(self._RT[self._ref_name][code])
	reg = stat.Regression(x,y, slope=self._slope)
	CF = reg.lin_robust()
        image.save_image(x,y,CF,sample_x=sample)
	return CF

    def align_ref(self, CF_RT):
	lib_file = self._path.library_file_ref
        library = imp.library_import(lib_file, self._info.csv)
        code_set = get_code_set(self._RT)
        x = []
        y = []
	RT_ref = collections.defaultdict(list)
        for sample in self._RT:
	    CF = CF_RT[sample]
	    for code in self._RT[sample]:
		RT_ref[code].append(self._RT[sample][code]*CF[0]+CF[1])
	for code in library:
            if code in RT_ref:
	        x.append(stat.calc_median(RT_ref[code]))
	        y.append(library[code]['RT'])
	reg = stat.Regression(x,y)
	CF_ref = reg.lin_robust()
	image = SaveImage(self._path.align_dir, sample_y='RT_ref') 
	image.save_image(x,y,CF_ref,sample_x='Reference')
	CF_new = {}
	for sample in self._runlist:
	    CF_new[sample] = (CF_RT[sample][0]*CF_ref[0], CF_RT[sample][1]*CF_ref[0]+CF_ref[1])
	return CF_new

#---end of class Align-----------------------------------------------------




class Calibrate(object):
    def __init__(self, project):
	self._project = project
	self._runlist = project.path.runlist_cal
	self._cal_file = project.path.runlist_file
	self._sep = project.info.csv.sep

    def calibrate(self):
	self.setup_data()
	self.align_samples()
	self.create_library()
	print 'library created'
	self.save_files()
	return

    def setup_data(self):
	create_dir(self._project.path)
	move_amdis(self._project.path)
	self.get_RT()
	self.remove_ignore()
	return

    def align_samples(self):
	align = Align(self._project, self._RT, self._runlist)
	self._CF = align.align()
	self.save_cal_file()
	return

    def save_cal_file(self):
	s = self._sep
	with open(self._cal_file, 'w') as cal_file:
	    for sample in self._runlist:
		CF = self._CF[sample]
	        cal_file.write('{0}{1}{2}{1}{3}\n'.format(sample, s, CF[0], CF[1]))
        return

    def create_library(self):
	library = Library(self._project, self._RT, self._CF)
	library.write_lib()
	return

    def save_files(self):
	write_RT = WriteData(self._project, 'RT', self._RT)
	write_RT.save_file()
	write_fit = WriteData(self._project, 'fit', self._fit)
	write_fit.save_file()
	return


    def get_RT(self):
	self._RT = {}
	self._fit = {}
	for item in self._runlist:
	    sample = imp.Sample(item, self._project.path, self._project.csv, CF=None, cal=1)
	    self._RT[item], self._fit[item] = sample.read_amdis(cal=1)
	return

    def remove_ignore(self):
        for sample in self._RT:
            try:
                for code in self._project.info.codes_ignore:
                    del self._RT[sample][code]
            except:
                pass
        return

#---End of Class Calibration--------------------------------------


class WriteData(object):
    def __init__(self, project, item, data_dict):
	self._file_name = project.path.align_data_file(item)
	self._dict = data_dict
	self._codelist = sorted(get_code_set(data_dict))
	self._write_line =project.info.csv.make_line
	self._sep = project.info.csv.sep

    def save_file(self):
	with open(self._file_name, 'w') as datafile:
	    datafile.write(self.header())
	    for sample in self._dict:
#		datafile.write('{0}{1}'.format(sample, self._sep))
	        datafile.write(self.line(sample))
	return

    def header(self):
	list =['Sample']+self._codelist
	return self._write_line((['Sample']+self._codelist))
#	header = 'Sample{0}'.format(self._sep)
#	for code in self._codelist:
#	    header += '{0}{1}'.format(code,self._sep)
#	header += '\n'
#	return header

    def line(self, sample):
	info = [sample]
#	line = '{0}{1}'.format(sample, self._sep)
	for code in self._codelist:
	    try:
		data_point = self._dict[sample][code]
	    except KeyError:
		data_point = 'ND'
	    info.append(data_point)
	return self._write_line(info)
#	    line += '{0}{1}'.format(data_point, self._sep)
#	line += '\n'
#	return line

#---End of Class WriteData----------------------------------


def linreg(x,y,slope):
    linfit = statistics.LinFit(x,y,slope=slope)
    return linfit.lin_fit()


def get_code_set(RT_dict):
    code_set = set()
    for sample in RT_dict:
        for code in RT_dict[sample]:
            code_set.add(code)
    return code_set

def move_amdis(path):
    if os.path.isfile(path.amdis_file):
        imp.amdis_batch(path)
        os.unlink(path.amdis_file)
    return

def create_dir(path):
    if not os.path.exists(path._project_dir):
        os.mkdir(path._project_dir)
    if not os.path.exists(path.amdis_dir):
        os.mkdir(path.amdis_dir)
    if not os.path.exists(path.align_dir):
        os.mkdir(path.align_dir)
    return

def main(project_name = None):
    if not project_name:
        import analyse
        project_name = analyse.get_project_name()
    print '{0}: read data'.format(project_name)
    project = pyquan.Project(project_name, init_file='pyquan.ini')
    calibrate = Calibrate(project)
    calibrate.calibrate()
    print('\a')
    return

if __name__=='__main__':
    status = main()
    sys.exit(status)
