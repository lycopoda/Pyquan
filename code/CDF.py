import getfile, os, sys
import numpy as np
from netCDF4 import Dataset

class CDF(object):
    def __init__(self, sample):
        cdf_dir = os.path.join('..','data')
        file_name = '{0}.cdf'.format(sample)
        cdf_file = getfile.get_file_name(cdf_dir, file_name)
        if not cdf_file:
            print('\nError: {0} not present in data folder'.\
                  format(file_name))
            sys.exit(2)
        self._CDF = Dataset(cdf_file, 'r')
        self._scan_time = np.array(self._CDF.variables\
                                   ['scan_acquisition_time'])
        
    def __enter__(self):
        return self
  
    def __exit__(self, exc_type, exc_value, traceback):
        self._CDF.close()
        return False

    def import_data(self):
        self._scan_index = self._CDF.variables['scan_index'][:]
        self._mass_values = np.rint(np.array(self._CDF.variables\
                                    ['mass_values'])).astype(int).tolist()
        self._intensity_values = np.array(self._CDF.variables\
                                          ['intensity_values'][:])
        return

    @property
    def scan_index(self):
        return self._scan_index

    @property
    def empty_TIC(self):
        return np.zeros(len(self._scan_time))

    @property
    def get_n_scans(self):
        return len(self._scan_time)

    def get_time(self, t):
        return self._scan_time[t]

    @property
    def scan_time(self):
        return self._scan_time

    def time_index(self, RT):
        return (np.abs(self._scan_time -RT)).argmin()
    
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
                i = mass_slice.index(m)
                intensity += intensity_slice[i]
            except ValueError:
                pass
        return intensity

