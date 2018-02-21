import sys

def bf(project, code=None, threshold=3):
    Backfill(project, threshold=threshold, code=code).RTdict()
    return

class Backfill():
    def __init__(self, project, threshold=3, code=None):
        self._project = project
        self._threshold = threshold
        self._code = code

    def RTdict(self):
        if not self._code:
            for code in self._project.lib.library:
                self.check_code(code)
        else:
            self.check_code(self._code)
        return

    def check_code(self, code):
        if self.enough(code):
            self.bf(code)
        return

    def enough(self, code):
        count = 0
        for sample in self._project.runlist:
            if code in self._project.RTdict[sample]:
                count += 1
        if count >= self._threshold:
            return True
        else:
            return False
            
    def bf(self, code):
        for sample in self._project.runlist:
            if not self._project.RTdict[sample].get(code, (None, 0))[0]:
                RT_lib = self._project.lib.RT(code)
                CF = self._project.CFdict[sample]
                self._project._RTdict[sample][code] = \
                ((RT_lib - CF[1]) / CF[0], 0)
        return



                


