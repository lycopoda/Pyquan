import sys, os, amdis, h5py
import numpy as np

def create_file(project):
    print(project.path.hdf5)
    f = h5py.File(project.path.hdf5, 'w')
    for sample in project.runlist:
        f.create_group(sample)
    return

class HDF5(object):
    def __init__(self, filename):
        self._f = h5py.File(filename)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self._f.close()

    @property
    def samplelist(self):
        return self._samplelist

    @property
    def codelist(self):
        return self._codelist

    @property
    def RTdict(self):
        return self._RTdict

    @property
    def fitdict(self):
        return self._fitdict

    @property
    def areadict(self):
        return self._areadict

    def save(self, sample, ID):
        fs = self._f[sample]
        for code in ID:
            if code in fs:
                del fs[code]
            fcode = fs.create_group(code)
            for item in ['area', 'RT', 'fit','x', 'y']:
                if item in ID[code]:
                    data = ID[code][item]
                    fcode.create_dataset(item, data=data)
            if 'param' in ID[code]:
                fparam = fcode.create_group('param')
                for peak in ID[code]['param']:
                    data=ID[code]['param'][peak]
                    try:
                        fparam.create_dataset(peak, data=data)
                    except TypeError:
                        pass
            if 'real_y' in ID[code]:
                freal = fcode.create_group('real_peak')
                y, index = ID[code]['real_y']
                freal.create_dataset('y', data=y)
                freal.create_dataset('index', data=index)
        return

    def get_project_data(self):
        self.makelists()
        self._RTdict = self.getdata('RT')
        self._fitdict = self.getdata('fit')
        self._areadict = self.getdata('area')
        return

    def makelists(self):
        self._samplelist = sorted(list(self._f.keys()))
        codeset = set()
        for sample in self._samplelist:
            [codeset.add(key) for key in self._f[sample].keys()]
        self._codelist = sorted(list(codeset))

    def getparam(self, sample, code=None):
        if not code:
            self.makelists()
            codelist = self._codelist
        else:
            codelist = [code]
        peakdict = {}
        for code in codelist:
            if code in self._f[sample]:
                fc = self._f[sample][code]
                peakdict[code] = {}
                try:
                    peakdict[code]['param'] = fc['param']['int'].value
                except KeyError:
                    try:
                        peakdict[code]['real_x'] = fc['real_x'].value
                        peakdict[code]['real_y'] = fc['real_y'].value
                    except KeyError:
                        pass
        return peakdict

    def getdata(self, item):
        datadict = dict.fromkeys(self._codelist)
        for code in self._codelist:
            datadict[code] = dict.fromkeys(self._samplelist)
            for sample in self._samplelist:
                try:
                    data = self._f[sample][code][item].value
                except KeyError:
                    data = 'ND'
                datadict[code][sample] = data
        return datadict
                    

class Data(object):
    def __init__(self, filename):
        self._f = h5py.File(filename)
        self._fs = self._f
        self._ID = {}
        
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self._f.close()


def recursive_load_dict(h5file, path):
    d = {}
    for key, item in h5file[path].items():
        if isinstance(item, h5py._hl.dataset.Dataset):
            d[key] = item.value
        elif isinstance(item, h5py._hl.group.Group):
            d[key] = recursive_load_dict(h5file, 
                               path='{0}{1}/'.format(path,key))
    return d

def data(filename, path='/'):
    with h5py.File(filename, 'r') as h5file:
        return recursive_load_dict(h5file, path='/')

       


class DataFiles(object):
    def __init__(self, project, sample):
        self._csv = project._csv
        self._itemlist = ["code","area","RT","fit","param",
                          "real_x","real_y", 'x', 'y']
        self._stylelist = ['str', 'float','float','int','list_float',
                           'list_int','list_int', 'float', 'float']
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
            data = ID.ID[item]
            datalist.append(data)
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
