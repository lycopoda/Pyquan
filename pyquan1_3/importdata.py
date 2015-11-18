import re, os.path, sys
from netCDF4 import Dataset
import numpy as np


def get_codeset(RT_dict):
    '''returns a set containing all second level keys
        in a two-level dictionary'''
    codeset=set()
    for sample in RT_dict:
        for code in RT_dict[sample]:
            codeset.add(code)
    return codeset

def amdis_batch(path):
    '''separate an AMDIS batch file into a file for each sample'''
    re_name=re.compile(r'([\w]+)(?=\.FIN)')
    data_dict = {}
    with open(path.amdis_file, 'r') as data:
        header = data.readline()
        for line in data:
            info =  line.split('\t')
            sample = re_name.search(info[0]).group(1)
            if sample: # in order to cope with empty lines
                if sample not in data_dict:
                    data_dict[sample]=[]
                data_dict[sample].append(line)
    for sample in data_dict:
        with open(path.amdis_file_sample(sample), 'w') as data:
            data.write(header)
            for i in data_dict[sample]:
                data.write(i)
    return

def get_ID(line, project_name):
    '''collect identification data: (1)project name, (2)sample name,
    (3) Correction factors for alignment''' 
    ID = {}
    ID['project'] = project_name
    runlist_local = line.strip().split(',')
    ID['sample'] = runlist_local[0]
    ID['CF'] = ([float(runlist_local[1]),float(runlist_local[2])])
    return ID


def library_import(library_file, csv):
    '''import reference library and stores it as a dictionary'''
    library={}
    with open(library_file, 'r') as lib:
        lib.readline()        
        for line in lib:
	    code, RT, lim, mass, name, source = csv.read_csv(line)[:6]
            code = correct_code(code)
            library[code]={}
            library[code]['RT'] = float(RT)
            library[code]['lim'] = float(lim)
            try:
		mass = mass.split('+')
                library[code]['mass'] = mass 
            except:
                print 'Mass in library file should be an integer'
                sys.exit(2)
            library[code]['name'] = name
            library[code]['source'] = source
    return library



def correct_code(code):
    for i in range(3):
        if code[0] == '0':
            code = code[1:]
    return code               
            
class Sample():
    def __init__(self, sample, path, csv, CF=None, cal=0):
        self._sample = sample
        self._path = path
        if cal==0:
            self._library = library_import(path.library_file, csv)
	else:
	    self._library = library_import(path.library_file_ref, csv)
        if CF:
            self._CF = CF

    @property
    def codeset(self):
	return self._codeset

    @property
    def sample(self):
        return self._sample
    
    @property
    def RT_dict(self):
        return self._RT_dict

    def RT_code(self, code):
	return self._RT_dict[code]

    @property
    def fit_dict(self):
	return self._fit_dict

    def fit_code(self, code):
	return self._fit_dict[code]

    def backfill(self):
        '''This function fills in estimated RT for compounds that are not
        recognized by AMDIS in this sample'''
        for code in self._library:
            if not code in self._RT_dict:
            #estimate RT, based on alignment and RT_ref
                RT_th = (self._library[code]['RT'] - self._CF[1])/self._CF[0]
                self._RT_dict[code] = (RT_th)
		self._codeset.add(code)
                self._fit_dict[code] = 'ND'
        #prepare intensity dictionary
        for code in self._RT_dict:
            self._time_dict[code] = []
            self._intensity_dict[code] = []
        return self._RT_dict            

    def check_time(self, code, RT):
        check = 0
        if code in self._library:
            RT_cor = RT*self._CF[0] + self._CF[1]
            RT_lib = self._library[code]['RT']
            RT_lim = self._library[code]['lim']
            if (RT_lib - RT_lim) < RT_cor < (RT_lib + RT_lim):
                check = 1
        return check
        
    def get_RT(self):
        self.read_amdis(cal=0)
    
    def read_amdis(self, cal=0):
        '''Reads AMDIS results data. It collects for each identified
        peak (1) code, (2) the RT with the best (3) fit within a specified
        time range from the library. If cal=1, no RT check is done'''
        self._RT_dict = {}
        self._fit_dict = {}
	self._codeset = set()
	try:
            with open(self._path.amdis_file_sample(self._sample),\
		  'r') as input_file:
                input_file.readline()
                for line in input_file:
                    info = line.split("\t")
                    code = correct_code(info[2].split(':')[0].split('?')[-1].strip())
                    RT = float(info[3])*60. #from minutes to seconds
                    fit = max(info[23:27])
                    check = 1
                    if cal == 0:
                        check = self.check_time(code, RT)
                    if check == 1:
                        if not code in self._RT_dict:
			    self._codeset.add(code)
                            self._RT_dict[code] = RT
                            self._fit_dict[code] = fit
                        elif self._fit_dict[code]<fit:
                            self._RT_dict[code] = RT
                            self._fit_dict[code] = fit
	except IOError:
	    print '{0} not in AMDIS results, check name in project file.'.format(self._sample)
	    sys.exit(2)
        #prepare intensity dictionary
        if cal == 0:
            self._time_dict = {}
            self._intensity_dict = {}
            for code in self._RT_dict:
                self._time_dict[code] = []
                self._intensity_dict[code] = []
        return self._RT_dict, self._fit_dict
        
    def write_data(self):
        with open(self._path.RT_file(self._sample), 'w') as RT_file:
            for code in sorted(self._RT_dict):
                RT_file.write('{0},{1}\n'.format(code, self._RT_dict[code]))
        with open(self._path.fit_file(self._sample), 'w') as fit_file:
            for code in sorted(self._fit_dict):
                fit_file.write('{0},{1}\n'.format(code, self._fit_dict[code]))
        return
    

class CDF(object):
    
    def __init__(self, sample):
        cdf_dir = os.path.join('..','data')
        file_list = os.listdir(cdf_dir)
        cdf_file = ()
        for f in file_list:
            if f[:-4].lower() == sample.lower():
                cdf_file = os.path.join(cdf_dir, f)
        self._CDF = Dataset(cdf_file, 'r')
        self._scan_time = np.array(self._CDF.variables['scan_acquisition_time'])                            
    def import_data(self):
        self._scan_index = self._CDF.variables['scan_index'][:]
        self._mass_values = np.rint(np.array(self._CDF.variables\
                                    ['mass_values'])).astype(int).tolist()
        self._intensity_values = np.array(self._CDF.variables['intensity_values'])
        return
    
    def getindex(self):
        return self._scan_index

    @property
    def empty_TIC(self):
        return np.zeros(len(self._scan_time))
    
    def get_n_scans(self):
        return len(self._scan_time)
          
    def get_time(self, t):
        return self._scan_time[t]

    @property    
    def scan_time(self):
        return self._scan_time


    def time_index(self, RT):
        i = (np.abs(self._scan_time -RT)).argmin()
        return i
    
    @property
    def total_TIC(self):
        return self._CDF.variables['total_intensity'][:]
    
    def slice(self, t):
        '''Collects intensity and mass data arrays at scan point'''
        start = self._scan_index[t]
        end = self._scan_index[t+1]
        mass_slice = self._mass_values[start:end]
        intensity_slice = self._intensity_values[start:end]
        return mass_slice, intensity_slice
    
    def intensity(self, t, mass):
        intensity = 0.
        mass_slice, intensity_slice = self.slice(t)
        for m in mass:
            try:
                m = int(m)
            except ValueError:
                print 'Error in reading mass ({0}),\
                       check mass list in library'.format(mass)
            i = mass_slice.index(m)
            if i:
                intensity += intensity_slice[i] 
            return intensity

    def get_total_TIC(self):
        return self._CDF.variables['total_intensity'][:]
        
    def close_cdf(self):
        del self._mass_values
        del self._intensity_values
        self._CDF.close()
        return

