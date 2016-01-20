import sys, os, re, init

class Project():
    def __init__(self, project_name):
		self._info = init.Info('pyquan.ini')
		self._path = init.Path(project_name, self._info)

    def amdis_name(self):
        return re.compile(r'([\w]+)(?=\.FIN)')

    def create_runlist(self):
        runset = set()
        if os.path.exists(self._path.amdis_file):
            runset = self.from_amdis_file()
        self.from_amdis_dir()
        if not runset:
            try:
                runset = self.from_amdis_dir()
            except:
                print 'AMDIS data missing'
                sys.exit(2)
        self.save_runlist(runset)
        return
	
    def save_runlist(self, runset):
        with open(self._path.runlist_file_cal, 'w') as runlist:
            for sample in sorted(runset):
                runlist.write(self._info.csv.make_line([sample, 'x']))
        return

    def from_amdis_dir(self):
        runset = set()
        for item in os.listdir(self._path.amdis_dir):
            if item.endswith('.txt'):
                runset.update([item[:-9]])
        return runset
	
    def from_amdis_file(self):
        runset = set()
        re_name = self.amdis_name()
        with open(self._patu.amdis_file, 'r') as amdis:
            amdis.readline()
            for line in amdis:
                info = line.split('\t')
                runset.update(re_name.search(info[0]).group(1))
		return runset


def main(project_name = None):
    if not project_name:
        project_name = sys.argv[1]
    project = Project(project_name)
    project.create_runlist()
    return 0

if __name__=='__main__':
	status = main()
	sys.exit(status)
