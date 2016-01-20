import sys, os, re, init

class Project():
    def __init__(self, project_name, info=None):
                if not info:
                   info= init.Info("pyquan.ini")
		self._info = info
		self._path = init.Path(project_name, self._info)


    def create_runlist(self):
        runset = self.from_amdis_file()
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
                runset.update([item[:-10]])
        return runset
	
    def from_amdis_file(self):
        import amdis
	comp = amdis.AmdisCompile()
        runset = set()
        if self._path.amdis_file:
            with open(self._path.amdis_file, 'r') as amdis_file:
                amdis_file.readline()
                for line in amdis_file:
                    info = line.split('\t')
                    runset.add(comp.sample_compile.\
		                  search(info[0]).group(1).lower())
	return runset

    def read_runlist(self):
        runlist = []
        with open(self._path.runlist_file_cal, 'r') as runfile:
            for line in runfile:
	        info = self._path._read_csv(line)
	        if info[1] in ['x', 'X']:
	            runlist.append(info[0].lower())
        return runlist

def CFdict(path, csv):
    import amdis
    CFdict = {}
    with open(path, 'r') as calfile:
        for line in calfile:
            info = csv.read_line(line)
            CFdict[amdis.correct_code(info[0])] = (float(info[-2]),
                                                   float(info[-1]))
    return CFdict

def main(project_name = None):
    if not project_name:
        project_name = sys.argv[1]
    project = Project(project_name)
    project.create_runlist()
    return 0

if __name__=='__main__':
	status = main()
	sys.exit(status)
