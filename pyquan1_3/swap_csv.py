import csv, sys

def swap(old=",", new=";"):
    csv_c = csv.CSV(sep=old)
    csv_sc = csv.CSV(sep=new)
    file_name = "..\library\library_ref_p1.csv"
    with open(file_name, 'r') as old:
        all_lines = old.readlines()
    with open(file_name, 'w') as new:
        for line in all_lines:
            info = csv_c.read_csv(line)
            new.write(csv_sc.make_line(info))
    return

def main():
    print 'start swap'
    swap()
    return

if __name__=='__main__':
    status = main()
    sys.exit(status)
