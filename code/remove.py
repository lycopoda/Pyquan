import init, sys, os, amdis
from argparse import ArgumentParser
'''Removes codes from the data files.
Either from one sample or from the whole project.'''

class RemoveCode():
    def __init__(self, path, info, code):
        self._path = path
        self._code = code
        self._csv = info.csv
        

    def remove_all(self):
        for sample in self._path.runlist_cal:
            print(sample)
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
                code = None
                try:
                    code = self._csv.read_line(lint)[0]
                except:
                    pass
                if code != self._code:    
                    data.write(line)

def get_info():
    arg_parser = ArgumentParser(description = \
                   'Remove peaks from data files and data images')
    arg_parser.add_argument('project_name', metavar='Project name',
            help='Project name')
    arg_parser.add_argument('sample', metavar='Sample name',
            help='Sample name or "all"')
    arg_parser.add_argument('code', metavar='Code', help='Compound code')
    options = arg_parser.parse_args()
    return options

def main():
    options = get_info()
    project_name = options.project_name.lower()
    sample = options.sample.lower()
    code = amdis.correct_code(options.code)
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
