import sys, amdis, os

class Library(object):
    def __init__(self, path, csv):
        self._path = path
        self._csv = csv
        self._lib = {}
        self._headerlist = ['code','RT','lim','mz','name','source']
        if os.path.exists(path):
            self.import_lib()

    @property
    def library(self):
        return self._lib

    def RT(self, code):
        return self._lib[code]["RT"]

    def lim(self, code):
        return self._lib[code]["lim"]

    def mz(self, code):
        return self._lib[code]["mz"]

    def name(self, code):
        return self._lib[code]["name"]

    @property
    def source(self, code):
        return self._lib[code]["source"]

    def import_lib(self):
        with open(self._path, 'r') as lib:
            lib.readline()
            for line in lib:
                self.read_line(line)
        return
           
    def read_line(self, line):
        info = self._csv.read_line(line)
        try:
            info[0] = amdis.correct_code(info[0])
        except:
            return None
        try:
            info[1] = float(info[1])
        except ValueError:
            info[1] = None
            return None
        try:
            info[2] = float(info[2])
        except ValueError:
            print('ERROR: in {0}, value for lim in code {1} is not a number \
                   or missing.'.format(self._path, info[0]))
            sys.exit(2)
        try:
            info[3] = [int(i) for i in info[3].split("+")]
        except:
            print('ERROR: in {0}, value for m/z in code {1} is wrong format.'\
                  .format(self._path, info[0]))
            print('It should be one integer, or more separate with "+".')
            sys.exit(2)
        self._lib[info[0]] = {}
        for i in range(1,len(self._headerlist)):
            self._lib[info[0]][self._headerlist[i]] = info[i]
        return 

    def makeline(self, code):
        info = [code]
        for item in self._headerlist[1:]:
            try:
                info_bit = self._lib[code][item]
                if item == 'mz':
                    info_bit = '+'.join([str(i) for i in info_bit])
            except KeyError:
                info_bit = ""
            info.append(info_bit)
        return self._csv.make_line(info)
 
    def write_library(self, path):
        RTlist = []
        nonRTlist = []
        for code in self._lib:
            try:
                RTlist.append((code, self._lib[code]['RT']))
            except KeyError:
                nonRTlist.append(code)
        RTlist.sort(key=lambda x: float(x[1]))
        codelist = [i[0] for i in RTlist]+nonRTlist
        with open(path, 'w') as lib_new:
            lib_new.write(self._csv.make_line(self._headerlist))
            for code in codelist:
                 lib_new.write(self.makeline(code))
        return  codelist
