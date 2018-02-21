import sys

class NormFiles(object):
    def __init__(self, project, normalize):
        self._project = project
        self._data = normalize._data
        self._normalize = normalize
        project.read_library()
        self._datadict = {}
        self._itemlist = ['RT','RT_ref','fit','area','area_norm']
        
    def writefiles(self):
        with open(self._project.path.area_norm_file, 'w') as norm,\
             open(self._project.path.data_norm_file, 'w') as data:
                 norm.write(self.header_areanorm())
                 data.write(self.header_data())
                 for code in self._project.lib.library:
                     norm.write(self.line_areanorm(code))
                     data.write(self.line_data(code))
        return

    def header_areanorm(self):
        header = ['code']
        for sample in self._project.runlist:
            header.append(sample)
        return self._project.csv.make_line(header)

    def header_data(self):
        line1 = ['sample']
        line2 = ['code']
        for sample in self._project.runlist:
            line1.extend([sample, '','','','',''])
            line2.extend(['RT','RT_ref','fit','area','area_norm'])
        for line in [line1, line2]:
            line = self._project.csv.make_line(line)
        return self._project.csv.make_line(line1+line2)

    def line_areanorm(self, code):
        line = [code]
        for sample in self._project.runlist:
            try:
                line.append(self._data._datadict[sample][code]['area_norm'])
            except KeyError:
                line.append('')
        return self._project.csv.make_line(line)

    def line_data(self, code):
        line = [code]
        for sample in self._project.runlist:
            for item in self._itemlist:
                try:
                    line.append(self._data._datadict[sample][code][item])
                except KeyError:
                    line.append('')
        return self._project.csv.make_line(line)
                   
