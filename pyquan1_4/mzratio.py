import sys, os, amdis


class CF(object):
    def __init__(self, project):
        self._project = project
        self.import_amdis()

    def CF(self, code):
        try:
            TIC = float(sum(self._amdisdict[code].itervalues()))
        except KeyError:
            print '{0} not in AMDIS library'.format(code)
            sys.exit(2)
        TIC_mz = 0.
        for mz in self._project._library._lib[code]['mz']:
            try:
                TIC_mz += self._amdisdict[code][mz]
            except KeyError:
                print 'ERROR: mz {0} not in mass spectrum of {1}'.\
                       format(mz, code)
                sys.exit(2)
        return TIC / float(TIC_mz)

    def import_amdis(self):
        self._amdisdict = amdis.read_intensity(self._project)
        return

        
