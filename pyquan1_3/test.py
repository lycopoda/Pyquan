import importdata as imp
import timeit, sys
import numpy as np

def create_cdf_class():
    sample = 'P2013157'
    cdf = imp.CDF(sample)
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
    print 'Time to run {0}: {1}'.format(str(function), time)
    return

def intensity():
    mass = [40]
    t = 1000
    cdf = create_cdf_class()
    cdf.import_data()
    #cdf.time_index(1000)
    cdf.intensity(1000, mass)
    return

def check_peak():
    import check_peak
#    time = min(timeit.Timer(check_peak.main).repeat(1,1))
#    print 'Time to run check_peak: {0}'.format(time)
    check_peak.main()
    return

def run_pyquan():
    import pyquan
    pyquan.main('glucose')
    return

def run_normalize():
    import normalize
    normalize.main('francois')
    return

def total_mass():
    import importdata
    mass = 40
#    min_mass = float(mass) - 0.4
#    max_mass = float(mass) + 0.4
    cdf = create_cdf_class()
    scan_index = cdf._CDF.variables['scan_index'][:]
    mass_list_float = cdf._CDF.variables['mass_values']
    mass_list = [int(round(m)) for m in mass_list_float[:]]
    index = mass_list.index(mass)
    print index
#    intensity_list = cdf._CDF.variables['intensity_values'][:]
#    overview = zip(mass_list[:],intensity_list[:])
#    y = []
#    for i in range(len(scan_index)-1):
#        start = scan_index[i]
#        end = scan_index[i+1]
#        for i in range(start, end):
#            if min_mass < mass_list[i] < max_mass:
#                y.append(intensity_list[i])
#                pass
#    print i
#    mass_dict = {}
#    for i, m in enumerate(mass_list):
#        mass = int(m)
#        if int(m+0.5)==mass:
#            mass += 1
#        mass_dict.setdefault(mass, [i])
#    for i in mass_dict:
#        print i
#    time_list = []
#    for i, time in enumerate(scan_index):
#        for i in range(time):
#            time_list.append(i)
#    mass_dict ={}
#    mass_dict[mass]=()
#    mass_start = ()
#    mass_end = ()
#    for i in range(len(zip_list)):
#        if i[2]>min_mass:
#            if not mass_start:
#                mass_start = i
#        if i[2]>max_mass:
#            mass_end = i-1
#            pass
#    mass_dict[mass] = (mass_start, mass_end)

             
    return            



def main():
#    time_process(create_cdf_class)
#    time_process(importdata)
#    time_process(time_index)
#    time_process(intensity)
    time_process(check_peak)
#    time_process(run_normalize)
#    time_process(total_mass)
#    time_process(run_pyquan)
    return

if __name__=='__main__':
    status = main()
    sys.exit(status)
