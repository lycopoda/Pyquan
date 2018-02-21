#check folder structure
#create folders and move code into folder structure

import sys, os, shutil
from os import listdir, mkdir
from os.path import isfile, join, exists

def main():
    for i in ('data', 'init', 'library', 'projects', 'code'):
        if not exists(i):
            mkdir(i)
    file_list = [f for f in listdir('.') if isfile(f)]
    for f in file_list:
        if f.endswith('.py') and f != 'setup.py':
             shutil.move(f, join('code', f))
        elif f.endswith('def'):
            shutil.copy(f, join('code', f))
            f_ini=f[:-4]+'.ini'
            shutil.move(f, join('init', f_ini))

    return

if __name__=='__main__':
    status = main()
    sys.exit(status)

