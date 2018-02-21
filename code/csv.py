import sys

class CSV(object):
    def __init__(self, sep=','):
        self._sep = sep

    @property
    def sep(self):
        return self._sep

    def read_line(self, line):
        dummy = None
        if '"' in line:
            item_list = line.split('"')
            line = item_list[0]
            dummy= {}
            for i in range(1,len(item_list)-1):
                key = 'dummy_{0}'.format(i)
                line +='dummy_{0}'.format(i)
                dummy[key] = item_list[i]
            line += item_list[-1]
        line_list = line.strip().split(self._sep)
        if dummy:
            for i in range(len(line_list)):
                if line_list[i] in dummy:
                    line_list[i] = dummy[line_list[i]]
        return line_list

    def read_transpose(self, file):
        info_list = []    
        with open(file, 'r') as input_file:
            for line in input_file:
                info_list.append(self.read_csv(line))
        info_trans = []
        for i in range(len(info_list[0])):
            item_list = []
            for x in range(len(info_list)):
                item_list.append(info_list[x][i])
            info_trans.append(item_list)
        return info_trans

    def make_line(self, info):
        line = None
        for i in range(len(info)):
            info[i] = str(info[i])
            if self._sep in info[i] and not info[i][0]=='"':
                info[i] = "".join(['"',str(info[i]),'"'])
        line = self._sep.join(info)
        line +="\n"
        return line

def transform(self, file_path, sep_old=";", sep_new=","):
    csv_old = CSV(sep_old)
    csv_new = CSV(sep_new)
    with open(file_path, 'r') as old:
        old_lines = old.readlines()
    with open(file_path, 'w') as new:
        for line in old_lines:
            line = csv_new.make_line(csv_old.read_line(line))
            new.write(line)
    return
