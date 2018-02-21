import sys, init, peak, os, library, warnings, project, datafiles, CDF
import peak_pars as pars
import noise_reduction as noise
from scipy.optimize import OptimizeWarning


class Sample(object):
    def __init__(self, project, sample):
        self._project = project
        self._sample = sample
        self._datafile = project._path.datafile(sample)
        self._cdf = CDF.CDF(sample)
        self._datadict = {}
        self._RTdict = project._RTdict[sample]

    @property
    def datafile(self):
        return self._datafile

    @property
    def scan_time(self):
        return self._cdf.scan_time

    @property
    def sample(self):
        return self._sample

    def time_index(self, RT):
        return self._cdf.time_index(RT)

    def get_time(self, t):
        return self._cdf.get_time(t)

    def intensity(self, t, mass):
        return self._cdf.intensity(t, mass)

    def close_cdf(self):
        self._cdf.close_cdf()
        return


def get_ID(project, sample, code, mass):
    sample_info = project._RTdict[sample][code]
    ID = peak.Peak_ID(sample, project, code, mass)
    try:
        ID.RT = sample_info[0]
        ID.fit = sample_info[1]
    except TypeError:
        ID.RT = None
        ID.fit = None
    return ID

def quantify(project):
    print('Read RT data from AMDIS results')
    project.read_library()
    project.get_CFdict()
    project.get_RTdict()
    datalines = []
    ID = {}
    for sample in project.runlist:
        line = 'Quantify peaks in {0}: '.format(sample)
        print(line, end=' ', flush=True)
        with CDF.CDF(sample) as cdf:
            cdf.import_data()
            for code in project._RTdict[sample]:
                print('\r{0}{1}   \t\t'.format(line, code), end='', flush=True)
                sys.stdout.flush()
                ID[code] = quantify_code(project, sample, code, cdf)
            with datafiles.HDF5(project.path.hdf5) as HDF5:
                    HDF5.save(sample, ID)
            print('\r{0}finished   \t\t'.format(line), flush=True)
    return 

def quantify_code(project, sample, code, cdf):
    with get_ID(project, sample, code, project._lib.mz(code)) as ID:
        peak_fit = peak.Code(ID, cdf, project)
        peak_fit.area(noise=project.noise, fit_peak=project.fit_peak)
    return ID.ID


def main(project_name):
    warnings.simplefilter("error", OptimizeWarning)
    proj = project.Project(project_name)
    proj.prepare_quantify()
    datafiles.create_file(proj)
    quantify(proj)
    return 0

if __name__=='__main__':
    import analyse
    project_name = analyse.get_project_name()
    status = main(project_name)
    sys.exit(status)
