import init, sys, os
import importdata as imp
'''Removes codes from the data files.
Either from one sample or from the whole project.'''

class RemoveCode():
    def __init__(self, path, info, code):
        self._path = path
        self._code = code
        

    def remove_all(self):
        for sample in self._path.runlist:
            print sample
            self.remove_code(sample)
        return
    
    def remove_code(self, sample):
        filename = self._path.datafile(sample)
        image_file = self._path.pyquan_fig_file(self._code, sample)
        if os.path.exists(image_file):
	    os.remove(image_file)
        with open(filename, 'r') as data_old:
            lines = data_old.readlines()
        with open(filename, 'w') as data:
            for line in lines:
                if ',' in line:
                    sep = ','
                elif ';' in line:
                    sep = ';'
                if line.split(sep)[0] != self._code:
                    data.write(line)


def main():
    project_name = sys.argv[1]
    sample = sys.argv[2]
    code = imp.correct_code(sys.argv[3])
    info = init.Info('pyquan.ini')
    path = init.Path(project_name, info)
    removecode = RemoveCode(path, info, code)
    if sample == 'all':
        removecode.remove_all()
    else:
        removecode.remove_code(sample)
    print('\a')
    return

if __name__=='__main__':
    status = main()
    sys.exit(status)
