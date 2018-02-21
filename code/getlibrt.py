import sys, init
from argparse import ArgumentParser

def get_arguments():
    arg_parser = ArgumentParser(description='Calculate library RT, based on\
    sample RT in minutes')
    arg_parser.add_argument('project_name', metavar='Project name',
    help='project name, similar to amdis file')
    arg_parser.add_argument('sample', metavar='sample name', \
    help='sample name')
    arg_parser.add_argument('RT', metavar='RT in minutes', \
    help='the RT you want to calculate the library for, in minutes')
    options = arg_parser.parse_args()
    project_name = options.project_name.lower()
    sample = options.sample.lower()
    RT = float(options.RT)
    return (project_name, sample, RT)

def main(project_name=None, sample=None, RT=None):
    if not project_name:
        project_name, sample, RT = get_arguments()
    info = init.Info('pyquan.ini')
    csv = info.csv
    with open(init.Path(project_name, info).runlist_file, 'r') as runlist:
        for line in runlist:
            sample_name, on, a, b = csv.read_line(line)
            if sample_name == sample:
                print(a,b)
                return (RT*60-float(b))*float(a)
    print('sample not in runlist')
    return


if __name__=='__main__':
    status = main()
    sys.exit(status)
