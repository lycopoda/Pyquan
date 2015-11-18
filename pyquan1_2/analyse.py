import calibrate, pyquan, normalize, sys
from argparse import ArgumentParser

def get_project_name():
    arg_parser = ArgumentParser(description = 'Analyse GC/MS data')
    arg_parser.add_argument('project_name', metavar='project name', help='project name, similar to amdis file')
    options = arg_parser.parse_args()
    return options.project_name

def main():
    project_name = get_project_name()
    calibrate.main (project_name=project_name)
    pyquan.main (project_name=project_name)
    normalize.main(project_name=project_name)
    print('\a')
    return 0

if __name__=='__main__':
    status = main()
    sys.exit(status)
