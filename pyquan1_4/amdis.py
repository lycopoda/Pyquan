import re, os, sys

class Compile(object):
    def __init__(self):
        self._sample_compile = re.compile(r'([\w]+)(?=\.FIN)')
        self._data_compile = re.compile(r'\([\d\s]*\)')
        self._intensity_compile = re.compile(r'([\d]+)')

    @property
    def sample_compile(self):
        """Regular expressions for AMDIS output files"""
        return self._sample_compile

    @property
    def data_compile(self):
        """Reads pairs from spectrum from amdis library"""
        return self._data_compile

    @property
    def intensity_compile(self):
        """Reads mz intensity from amdis library"""
        return self._intensity_compile

    def get_sample(self,line):
        """Extracts sample name from AMDIS output files"""
        return self.sample_compile.search(line.split('\t')[0]).group(1).lower()

def get_compound(line):
    """Extract code and compound from AMDIS output files"""
    if line[:4] == 'NAME':
        try:
           info = line.strip().split(':')
           code = correct_code(info[1].lstrip())
           compound = info[2].lstrip()
           return code, compound
        except IndexError:
#            print '"{0}" does not have a valid code'.format(info[1])
#            print 'Code should end with ":"'
             pass
    return None, None


def correct_code(code):
    """Removes initial 0's in AMDIS codes (used to keep AMDIS library sorted
    in the AMDIS software
    """
    for i in range(len(code)):
        if code[0] == '0':
            code = code[1:]
        else:
            break
    return code

def read_intensity(project):
    """Reads AMDIS library, and returns a dictionary with for each
    compound the intensity per mass.
    """
    intensity = {}
    with open(project.path.library_amdis, 'r') as amdis:
        for line in amdis:
            code, compound = get_compound(line)
            if code:
                try:
                    intensity[amdis_code._code]=amdis_code.intensity 
                except:
                    pass
                amdis_code = AmdisCode(project, code)
            elif line[0]=='(':
                amdis_code.read_line(line)
        if amdis_code:
            intensity[amdis_code._code] = amdis_code.intensity
    return intensity

def read_compounds(path):
    """Extracts code and compound information from the AMDIS library"""
    code_dict = {}
    with open(path, 'r') as amdis:
        for line in amdis:
            code, compound = get_compound(line)
            if code:
                if code in code_dict:
                    print '{0} double in AMDIS library'.format(code)
                    sys.exit(2)
                code_dict[code]=compound
    return code_dict

def batch(path):
    """Separates an AMDIS batch file into a file for each sample.
    These samples are stored in an amdis folder, with the project  folder."""
    data_dict =  {}
    comp = AmdisCompile()
    with open(path.amdis_file, 'r') as data:
        header = data.readline()
        sample_dict = {}
	for line in data:
            sample = read_line_batch(line, comp).lower()
            if not sample in sample_dict:
                sample_dict[sample] = []
            sample_dict[sample].append(line)
    return sample_dict, header
	        
def read_line_batch(line, comp):
    info = line.split("\t")
    sample = None
    sample = comp.sample_compile.search(info[0]).group(1).lower()
    return sample

class Sample(object):
    def __init__(self, amdis_file, library=None, CF=None):
        self._file = amdis_file
        self._data = {}
        self._comp = Compile()
        self._codeset = set()
        self._lib = library
        self._CF = CF

    
    def data(self, cal=False):
        with open(self._file, 'r') as output:
            output.readline()
            for line in output:
                code, RT, fit = self.read_line(line)
                check = True
                if not cal:
                    check = self.check_time(code, RT)
                if check:
                    self.add_ID(code, RT, fit)
        return self._data

    def add_ID(self, code, RT, fit):
        self._codeset.add(code)
        try:
            if fit < self._data[code][1]:
                return
        except KeyError:
            pass
        self._data[code] = (RT,fit)
        return
            
    def read_line(self, line):
        info = line.split("\t")
        code = correct_code(info[2].split(":")[0].split("?")[-1].strip())
        RT = float(info[3])*60. #from minutes to seconds
        fit = max(info[23:27])
        return code, RT, fit

    def check_time(self, code, RT):
        try:
            RT_ref = RT * self._CF[0] + self._CF[1]
            return abs(self._lib.RT(code) - RT_ref) < self._lib.lim(code) 
        except KeyError:
            return False

    def back_fill(self, code, CF):
        self._RT[code] = (self._library.RT(code) - CF[1])/CF[0]
        self._fit[code] = "ND"
        return


class AmdisCode(object):
    """
    Reads mass spectrum data from AMDIS library.
    It creates a dictionary with intensity data
    for each m/z.
    """

    def __init__(self, project, code):
        self._code = code
        self._intensity = {}
        self._mzlim = project.info.mass_limits
        self._comp = Compile()
        


    def read_line(self, line):
        """Adds intensity data to dictionary"""
        spectrum = re.findall(self._comp.data_compile, line)
        for i in spectrum:
            mz, intensity = re.findall(self._comp.intensity_compile,i)
            if self._mzlim[0] <= int(mz) <= self._mzlim[1]:
                self._intensity[int(mz)] = int(intensity)
        return

    @property
    def intensity(self):
        return self._intensity

