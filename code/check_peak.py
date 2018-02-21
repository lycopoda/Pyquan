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

    @property
    def runlist(self):
        return self._runlist


def main():
    check_peak = CheckPeak()
    project = proj.Project_cp(check_peak.projectname, check_peak)
    quantify.quantify(project)
    return

if __name__=='__main__':
    status = main()
    sys.exit(status)
