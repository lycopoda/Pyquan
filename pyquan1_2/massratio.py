import re, sys, os
import importdata as imp
reload(imp)


class AmdisCode(object):
    def __init__(self, code):
        self._code = code
        self._intensity = {}
        self._redata = re.compile(r'\([\d\s]*\)')
        #self._redata = re.compile(r'\(([\d+\s]*)\)')
        self._reintensity = re.compile(r'([\d]+)')
        #self._reintensity=re.compile(r'([\d]+)(?:[\s]+)([\d]+)')
        
    @property
    def intensity(self):
        return self._intensity
    
    def read_line(self, line):
        spectrum = re.findall(self._redata, line)
        for i in spectrum:
            mass, intensity = re.findall(self._reintensity,i)
            self._intensity[mass] = int(intensity)
        return
    

class Library(object):
    def __init__(self, library_amdis, min_mass, max_mass, library_project, csv):
        self._lib_amdis = library_amdis
        self._lib_proj = library_project
        self._min_mass = min_mass
        self._max_mass = max_mass
        self._csv = csv
        self.import_lib_amdis()
        self.read_library_project()
        
    def import_lib_amdis(self):
        self._amdis_dict = {}
        code = None
        amdis_code = None
	if not os.path.exists(self._lib_amdis):
	    print 'AMDIS library does not exist, check name in pyquan.ini file'
	    sys.exit(2)
        with open(self._lib_amdis, 'r') as amdis:
            for line in amdis:
                if line[:4] == 'NAME':
                    if code:
                        self._amdis_dict[code] = amdis_code.intensity
                    code = imp.correct_code(line.split(':')[1].strip())
                    amdis_code = AmdisCode(code)
                elif line[0] == '(':
                    amdis_code.read_line(line)
            self._amdis_dict[code] = amdis_code.intensity
        return

    def CF(self, code):
	try:
	    CF = self._CF[code]
	except KeyError:
	    CF = 'key'
	return CF

    def get_CF_old(self, code, mass):
	print type(mass)
        print 'code: {0}\tmass: {1}'.format(code, mass)
	TIC = float(sum(self._amdis_dict[code].itervalues()))
	return TIC / self._amdis_dict[code][mass]

    def get_CF(self, code, mass):
	try:
            TIC = float(sum(self._amdis_dict[code].itervalues()))
	except KeyError:
	    CF = 'AMDIS'
	mass = mass.split('+')
	TIC_m = 0.
        try:
            for m in mass:
	        TIC_m += self._amdis_dict[code][m]
		CF = TIC / TIC_m
	except KeyError:
	    CF = 'mass'
	return TIC / TIC_m
        
    def read_library_project(self):
        self._CF = {}
        with open(self._lib_proj, 'r') as lib:
            lib.readline()
            for line in lib:
		try:
			code, RT, lim, mass, name, source = \
					self._csv.read_csv(line)[:6]
		except ValueError:
		    print 'corrupted project library file:'
		    print line
		    sys.exit(2)
		code = imp.correct_code(code.strip())
  	        self._CF[code] = self.get_CF(code, mass)
        return
