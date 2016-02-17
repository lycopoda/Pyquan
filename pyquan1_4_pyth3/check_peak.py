import sys, init, quantify
import project as proj


class CheckPeak(object):
    def __init__(self):
        self._inifile = 'check_peak.ini'
        self._info = init.Info(self._inifile)
        self._projectname = self._info.project_name_check
        self._sample = self._info.sample_check
        self._code = self._info.code_check
        self._RT = self._info.RT_check
        self._fit_peak = self._info.fit_peak

    @property
    def info(self):
        return self._info

    @property
    def projectname(self):
        return self._projectname

    @property
    def sample(self):
        if not self._sample == 'all':
            return self._sample
        return None
 
    @property
    def RT(self):
        return self._RT
    
    @property
    def code(self):
        return self._code


    def runlist(self, runlist, runlistfile):
        if self._sample.lower() == 'all':
            samplelist = runlist
        elif self._sample in runlist:
            samplelist = [self._sample]
        else:
            print('ERROR: {0} not in sample list of {1}'.\
                  format(self._sample, self._projectname))
            print('Either mistype in {0} or {1} not selected in {2}'.\
                  format(self._inifile, self._sample, runlistfile))
            sys.exit(2)
        return samplelist

def main():
    check_peak = CheckPeak()
    project = proj.Project(check_peak.projectname, check_peak=check_peak)
    quantify.quantify(project)
    return

if __name__=='__main__':
    status = main()
    sys.exit(status)
