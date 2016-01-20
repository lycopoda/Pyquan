import sys, os, ConfigParser


class Info(object):
    def __init__(self, init_file):
        self._init_file = init_file
        self._path = os.path.join('..','init', init_file)
        parser = ConfigParser.ConfigParser()
        parser.read(self._path)
        self._init = parser
        
    @property
    def init_file(self):
        return self._path
        
    @property
    def init_backup(self):
        backup = self._init_file[:-4]+'.def'
        return backup
        
#---CSV------------------------------------------------------------------------
    @property
    def csv(self):
        import csv
        reload(csv)
        sep =  self._init.get('CSV', 'separator')
        if not sep:
            print 'give CSV separator in pyquan.ini file'
            sys.exit(2)
        CSV = csv.CSV(sep=sep)
        return CSV

#---Library--------------------------------------------------------------------
    @property
    def library_ref(self):
        return self._init.get('Library', 'library_ref')
        
    @property
    def library_amdis(self):
        return self._init.get('Library', 'library_amdis')

#---Peak par info---------------------------------------------------------------

    def p_order(self):
        try:
            return self._init.getint('Peak_fit', 'min_peak_dist')
        except:
            print 'min_peak_dist in init file should be an integer'
            sys.exit(2)
            
    def thresh(self):
        try:
            thresh = self._init.getfloat('Peak_fit', 'max_valley')
            if not 0<=thresh<=1:
                print 'max_valley should be a number between 0 and 1'
                sys.exit(2)
            return thresh
        except:
            print 'max_valley in init file corrupted,\
                    should be an floating number between 0 and 1'
    
    @property
    def peak_window(self):
	window = self._init.get('Peak_fit', 'peak_window')
        try:
            window = self._init.getint('Peak_fit', 'peak_window')
        except:
            print 'define peak_window in init file, default=120'
            sys.exit(2)
        if not window>0:
            print 'peak_window should be an positive integer'
            sys.exit(2)
        return window
                    
#---Smoothing info--------------------------------------------------------------
    
    def sm_meth(self):
        methods= ['savgol', 'mov_av']
        method = self._init.get('Smoothing', 'method')
        if method:
            if method not in methods:
                print 'smoothing method mistyped or not available'
                sys.exit(2)
            return method
            
    def sm_order(self):
        try:
            return self._init.getint('Smoothing', 'order')
        except:
            print 'Smooth order corrupt in .ini file, should be an integer'
            sys.exit(2)

        
    def sm_len(self):
        try:
            item = self._init.getint('Smoothing', 'window_len')
            if item & 0x1 != 1:
                print 'windows should be an odd number'
                sys.exit(2)
        except:
            print 'Smoothing window corrupt in .ini file, should be an odd integer'
            sys.exit(2)
        return item
        
    def sm_type(self):
        type_list = ['flat','hanning','hamming','bartlett','blackman']
        item = self._init.get('Smoothing','window_type')
        if not item in type_list:
            print 'wrong name for window_type in init file'
            sys.exit(2)
        return item
                
#---Base line correction--------------------------------------------------------

    @property
    def bsl_deg(self):
        return self._init.getint('Data_normalization', 'deg_bsl')
        
    @property
    def bsl_window(self):
        return self._init.getint('Data_normalization', 'window_bsl')
            
#---Normalization---------------------------------------------------------------
    @property
    def norm_method(self):
	answer = ['tic','sum']
        method = self._init.get('Data_normalization', 'method').lower()
	if method.isspace():
	    return None
        return  method
        
    @property
    def mass_limits(self):
        try:
            min_mass = self._init.getint('Data_normalization', 'min_mass')
            max_mass = self._init.getint('Data_normalization', 'max_mass')
        except:
            print 'Mass limits in pyquan.ini file should be integer numbers'
            sys.exit(2)
        return min_mass, max_mass
       
    @property
    def TIC_images(self):
	answer = ['yes', 'no']
        value = self._init.get('Data_normalization', 'TIC_images').lower()
	if not value in answer:
	    print '\n'
	    print 'Wrong value in pyquan.ini file (TIC_images), should be yes or no.'
	    sys.exit(2)
        return value


#---Calibration-----------------------------------------------------------------
    @property
    def sample_ref(self):
        try:
            item = self._init.getint('Alignment', 'sample_ref')
        except:
            print 'sample_ref should be an integer'
            sys.exit(2)
        return item

    @property
    def slope(self):
	try:
	    slope_fit = self._init.get('Alignment', 'slope_var')
	except:
	    print 'ini_file corrupted'
	    sys.exit(2)
	possibility = ['yes', 'no']
	if slope_fit not in possibility:
	    print 'Wrong parameter in pyquan.ini. Should be yes or no in slope_var'
	    sys.exit(2)
	return slope_fit
        
    @property
    def codes_ignore(self):
        return self._init.get('Alignment', 'codes_ignore').split(',')
    
    @property
    def auto_RT(self):
        return self._init.get('Alignment', 'auto_RT')
        
    @property
    def refine_factor(self):
        try:
            refine_factor = self._init.getfloat('Alignment', 'refine_factor')
        except:
            refine_factor = 1.
        return refine_factor

    @property
    def min_fit(self):
        try:
            min_fit = self._init.getint('Alignment', 'min_fit')
        except:
            print 'Value for min_fit should be an integer'
            sys.exit(2)
        return min_fit
                
#---Check Peak------------------------------------------------------------------
    @property
    def project_name_check(self):
        return self._init.get('Project', 'project_name')
    
    @property
    def code_check(self):
        return self._init.get('Peak_information', 'code')
        
    @property
    def sample_check(self):
        return self._init.get('Peak_information', 'sample_name').lower()
        
    @property
    def RT_check(self):
        try:
            RT = self._init.getfloat('Peak_information', 'peak_RT')*60. #from minutes to seconds
        except:
            RT = None
        return RT 
    
    @property
    def fit_peak(self):
        fit = self._init.get('Peak_fit', 'fit_peak')
        if fit:
            fit = fit.lower()
        if not fit in ['yes', 'no']:
            print 'fit_peak in check_peak.ini file should be either yes or no'
            sys.exit(2)
        return fit
                                


class Path():
    '''Create directories and filenames to store RT, fit, peak parameter and area data'''
    def __init__(self, project_name, info):
        self._project = project_name
        self._project_dir = os.path.join('..','projects', project_name)
        self._info = info
        self._read_csv = info.csv.read_line 
        
#---Directories-----------------------------------------------------------------
    @property
    def root_dir(self):
        return os.path.join('..', 'projects')

    @property
    def project_dir(self):
        return self._project_dir

    @property
    def project_dir(self):
        return self._project_dir

    @property
    def library_dir(self):
        return os.path.join('..', 'library')
    
    @property
    def align_dir(self):
        return os.path.join(self._project_dir, 'alignment')
        
    @property
    def amdis_dir(self):
        return os.path.join(self._project_dir, 'amdis')
        
    @property
    def data_dir(self):
        return os.path.join(self._project_dir, 'data')
        
    @property
    def images_dir(self):
        return os.path.join(self._project_dir, 'images')
        
    @property
    def init_dir(self):
        return os.path.join('init')
        
    @property
    def norm_dir(self):
        return os.path.join(self._project_dir, 'normalization')
        
#---files-----------------------------------------------------------------------
    
    @property
    def runlist_file(self):
        return os.path.join(self._project_dir, '{0}_cal.csv'.format(self._project))
        
#    @property
#    def runlist(self):
#        runlist=[]
#        try:
#            with open(self.runlist_file, 'r') as runfile:
#                for line in runfile:
#                    info=self._csv    
#                    runlist.append(self._info.csv.read_csv(line)[0])
#        except:
#            print 'Runlist corrupt, run calibration again'
#            sys.exit(2)
#        return runlist
    
    @property
    def runlist_file_cal(self):
        return os.path.join(self.root_dir,'{0}.csv'.format(self._project))

    @property
    def runlist_cal(self):
        import runlist
	run = runlist.Project(self._project)
	try:
	    run_list = run.read_runlist()
	except:
	    run.create_runlist()
	    run_list = run.read_runlist()
	return run_list

    @property
    def library_file(self):
        return os.path.join(self._project_dir, 'library_{0}.csv'.format(self._project))
    
    @property
    def library_file_ref(self):
        return os.path.join('..', 'library', self._info.library_ref)
    
    @property
    def library_amdis(self):
        return os.path.join('..', 'library', self._info.library_amdis)

    def datafile(self, sample):
        return os.path.join(self.data_dir, '{0}_data.csv'.format(sample))

    @property
    def RT_file(self):
        return os.path.join(self._project_dir,
			'{0}_RT.csv'.format(self._project))

    @property
    def RT_ref_file(self):
	return os.path.join(self._project_dir,
			'{0}_RT_ref.csv'.format(self._project))

    @property
    def area_file(self):
	return os.path.join(self._project_dir,
			'{0}_area.csv'.format(self._project))

    @property
    def area_norm_file(self):
	return os.path.join(self._project_dir,
			'{0}_area_norm.csv'.format(self._project))

    @property
    def data_norm_file(self):
        return os.path.join(self._project_dir,
                        '{0}_data.csv'.format(self._project))
 
    @property
    def fit_file(self):
        return os.path.join(self._project_dir,
			'{0}_fit.csv'.format(self._project))

    def output_norm_file(self, data='data'):
	name = '{0}_{1}.csv'.format(self._project,data)
	return os.path.join(self._project_dir, name)

    @property
    def output_file(self):
        return os.path.join(self.__project_dir,
			'{0}_area_norm.csv'.format(self._project))
        
    @property
    def norm_fit_file(self):
        return os.path.join(self._project_dir,
			'{0}_fit.csv'.format(self._project))
        
    @property
    def norm_RT_file(self):
        return os.path.join(self._project_dir,
			'{0}_RT.csv'.format(self._project))
        
    @property
    def norm_RT_ref_file(self):
        return os.path.join(self._project_dir,
			'{0}_RT_ref.csv'.format(self._project))
        
    @property
    def norm_data_file(self):
	return os.path.join(self._project_dir,
			'{0}_area.csv'.format(self._project))

    @property
    def RT_database_file(self):
	return os.path.join('..', 'library', 'RT_database.csv')

    @property
    def amdis_file(self):
        import getfile
	file_name = "{0}_AMDIS.txt".format(self._project)
	return getfile.get_file_name(self.root_dir, file_name)
        
    def pyquan_fig_file(self, code, sample):
        return os.path.join(self.images_dir,'{0}_{1}.png'.format(code, sample))
        
    def norm_fig_file(self, sample, part):
        return os.path.join(self.norm_dir,'{0}_{1}.png'.format(sample, part))
        
    def amdis_file_sample(self, sample):
        import getfile
        file_name = "{0}_amdis.txt".format(sample)
        file_name = getfile.get_file_name(self.amdis_dir, file_name,
                                          always="true")
        return file_name
#        file_list = os.listdir(self.amdis_dir)
#	file_name = None
#        for f in file_list:
#            if f[:-10].lower() == sample.lower():
#               file_name = os.path.join(self.amdis_dir, f)
#	if not file_name:
#            file_name =os.path.join(self.amdis_dir, '{0}_amdis.txt'.format(sample.lower()))
#        return file_name
    @property    
    def align_data_file(self):
        return os.path.join(self.align_dir,'RT.csv')

    @property
    def align_ref_file(self):
	return os.path.join(self.align_dir,'reference.png')

        
