import sys, os, amdis

def header(self):
    return 

class DataFiles(object):
    def __init__(self, project, sample):
        self._csv = project._csv
        self._itemlist = ["code","area","RT","fit","param",
                          "real_x","real_y"]
        self._stylelist = ['str', 'float','float','int','list_float',
                           'list_int','list_int']
        self._path = project._path.datafile(sample)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    @property
    def header(self):
        return self._csv.make_line(self._itemlist)

    def dataline(self, ID):
        datalist = []
        for item in self._itemlist:
            datalist.append(ID.ID[item])
        return self._csv.make_line(datalist)
    
    def getIDs(self):
        IDs = {}
        with open(self._path, 'r') as datafile:
            datafile.readline()
            for line in datafile:
               code, ID = self.ID(line)
               IDs[code] = ID
        return IDs

    def ID(self, line):
        info = self._csv.read_line(line)
        ID = {}
        for i in range(1,len(self._itemlist)):
            if 'None' in info[i]:
                info[i] = ''
            elif self._stylelist[i] == 'float':
                info[i] = float(info[i])
            elif self._stylelist[i] == 'int':
                info[i] = int(info[i])
            elif self._stylelist[i] == 'list_float':
                infolist = []
                for item in info[i].split(' '):
                    if item:
                        infolist.append(float(item))
                info[i] = infolist
            elif self._stylelist[i] == 'list_int':
                infolist = []
                for i in info[i].split(' '):
                    infolist.append(int(i))
                info[i] = infolist
            ID[self._itemlist[i]] = info[i]
        return amdis.correct_code(info[0]), ID

    def code(self, line):
        return amdis.correct_code(self._csv.read_line(line)[0])

    def read_file(self):
        data = {}
        with open(self._path, 'r') as datafile:
            datafile.readline()
            for line in datafile:
                code, ID = self.ID(line)
                data[code] = ID
        return data

    def make_file(self):
        with open(self._path, 'w') as datafile:
            datafile.write(self.header)
        return

    def write_data(self, ID):
        with open(self._path, 'a') as datafile:
            datafile.write(self.dataline(ID))
        return

    def update_file(self, ID):
        with open(self. _path, 'r') as data_old:
            lines = data_old.readlines()
        with open(self._path, 'w') as data_new:
            for line in lines:
                info = self._csv.read_line(line)
                if info[0] == ID.ID['code']:
                    line = self.dataline(ID)
                data_new.write(line)
        return
