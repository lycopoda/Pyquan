import amdis, os, sys, init, operator

'''If lib exists, update all compound names, and add new codes at bottom.
If lib not exists, create new lib with that name.
Give message that (some) compounds need a RT'''
def update_library(amdis_path, lib_path, csv):
    amdis_dict = amdis.read_compounds(amdis_path)
    info_old = None
    mz_dict = amdis.read_intensity(amdis_path)
    #open library if exists, and check compound name
    if os.path.exists(lib_path):
        with open(lib_path, 'r') as lib_old:
            lib_old.readline()
	    info_old = lib_old.readlines()
        info_old, amdis_dict = scan_amdis(info_old, amdis_dict,csv)
    with open(lib_path, 'w') as lib_new:
        if not info_old:
            lib_new.write(csv.make_line(['Code','RT','Limit','m/z','Name',
                                         'Source']))
        else:
            for line in info_old:
                if line[0] == 293:
                    print(line)
                    sys.exit(2)
                try:
                    spectrum = mz_dict[line[0]]
		    if not all(m in spectrum for m in line[3].split("+")):
                        print('m/z {0} not in mass spectrum of {1},' \
                              .format(line[3],line[0]),)
                        line[3] = max(spectrum.iteritems(), \
                                      key=operator.itemgetter(1))[0]
                        print('m/z changed to {0}'.format(line[3]))
                except KeyError:
                    pass  
	        lib_new.write(csv.make_line(line))
        if amdis_dict:
	    for code in amdis_dict:
                mass = max(mz_dict[code].iteritems(),
                       key=operator.itemgetter(1))[0]
	        lib_new.write(csv.make_line([amdis.correct_code(code),"","",
                                             mass,"",amdis_dict[code],""]))
    return
	        
def scan_amdis(info_old, amdis_dict, csv):
    from operator import itemgetter
    for i in range(len(info_old)):
        info_old[i] = csv.read_line(info_old[i])
        try:
            info_old[i][1] = float(info_old[i][1])
        except:
            pass
	info_old[i][0] = amdis.correct_code(info_old[i][0])
	compound = amdis_dict.pop(info_old[i][0], None)
	if compound:
	    info_old[i][4] = compound
	else:
	    print('{0} not in AMDIS library'.format(info_old[i][0]))
    return sorted(info_old, key=itemgetter(1)), amdis_dict
	

def make_path(directory, file_name, extension='csv'):
    if not '.' in file_name:
        file_name += '.{0}'.format(extension)
    return os.path.join(directory, file_name)

def main():
    info = init.Info('pyquan.ini')
    path = init.Path('dummy',info)
    try:
        amdis, lib = sys.argv
        amdis_path = make_path(path.library_dir, amdis, extension='msl')
        lib_path = make_path(path.library_dir, lib, extension='csv')
    except:
        print('AMDIS file, and library file defined in pyquan.ini are used')
        amdis_path = path.library_amdis
        lib_path = path.library_file_ref
    update_library(amdis_path, lib_path, info.csv)
    print('{0} created or updated'.format(lib_path))
    return

if __name__=='__main__':
     status = main()
     sys.exit(status)    
