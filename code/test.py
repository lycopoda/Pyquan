import CDF, warnings
import timeit, sys
import numpy as np
from scipy.optimize import OptimizeWarning
from matplotlib import pyplot as plt

class Image(object):
    def __init__(self):
        plt.figure()

    def __enter__(self):
        return

    def __exit__(self, type, value, traceback):
        plt.close()
        return

    def plot(self, x, y):
        plt.plot(x,y)
        plt.savefig('figure.png')
        return

def save_image():
    x= [1.]
    y=[1.]
    image = Image()
    with image:
        for i in range(100):
            image.plot(x,y)
#    for i in range(100):
#        plt.figure()
#        plt.plot(x,y)
#        plt.savefig('figure.png')
#        plt.close()
    return

def create_cdf_class():
    sample = 'P2013157'
    cdf = CDF.CDF(sample)
    return cdf

def importdata():
    cdf = create_cdf_class()
    cdf.import_data()
    return

def time_index():
    cdf = create_cdf_class()
    cdf.time_index(1000)
    return

def time_process(function):
    time = min(timeit.Timer(function, setup="gc.enable()").repeat(1,1))
    print('Time to run {0}: {1}'.format(str(function), time))
    return

def intensity():
    mass = [40]
    t = 1000
    cdf = create_cdf_class()
    cdf.import_data()
    cdf.intensity(1000, mass)
    return

def check_peak():
    import check_peak
    check_peak.main()
    return

def run_pyquan():
    import analyse
    analyse.main('francois')
    return

def run_quantify():
    import quantify
    quantify.main('brabant')

def run_normalize():
    import normalize
    normalize.main('francois')
    return

def run_calibrate():
    import calibrate
    calibrate.main('brabant')
    return

def total_mass():
    import importdata
    mass = 40
    cdf = create_cdf_class()
    scan_index = cdf._CDF.variables['scan_index'][:]
    mass_list_float = cdf._CDF.variables['mass_values']
    mass_list = [int(round(m)) for m in mass_list_float[:]]
    index = mass_list.index(mass)
    print(index)
    return            

def array():
    import numpy as np
    x=list(range(1000))
    x=np.array(x)
    x=x/60.
    return

def main():
    warnings.simplefilter('error', OptimizeWarning)
#    time_process(create_cdf_class)
#    time_process(importdata)
#    time_process(time_index)
#    time_process(intensity)
#    time_process(check_peak)
#    time_process(run_normalize)
#    time_process(total_mass)
    time_process(run_quantify)
#    time_process(run_pyquan)
#    time_process(run_calibrate)
#    time_process(save_image)
    return

if __name__=='__main__':
    status = main()
    sys.exit(status)
