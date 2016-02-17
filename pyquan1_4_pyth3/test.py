import CDF
import timeit, sys
import numpy as np

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
    quantify.main('francois')

def run_normalize():
    import normalize
    normalize.main('francois')
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



def main():
#    time_process(create_cdf_class)
#    time_process(importdata)
#    time_process(time_index)
#    time_process(intensity)
#    time_process(check_peak)
#    time_process(run_normalize)
#    time_process(total_mass)
    time_process(run_quantify)
#    time_process(run_pyquan)
    return

if __name__=='__main__':
    status = main()
    sys.exit(status)
