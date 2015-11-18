import init, sys
from argparse import ArgumentParser
reload(init)


def main():
    arg_parser = ArgumentParser(description = 'Restore ini file')
    arg_parser.add_argument('ini_file', metavar='type of ini file', help='pyquan or check_peak')
    options = arg_parser.parse_args()
    name = '{0}.ini'.format(options.ini_file)
    info = init.Info(name)
    with open(info.init_file, 'w') as new, open(info.init_backup, 'r') as backup:
        for line in backup:
            new.write(line)
    return 0

def set_default(ini):
    info = init.Info('{0}.ini'.format(ini)
    with open(info.init_file, 'w'

def check_peak():
    return

def pyquan():
    return
    
if __name__=='__main__':
    status = main()
    sys.exit(status)
