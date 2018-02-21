#!/usr/bin/python

import os, sys, calibrate, quantify, normalize, analyse
from tkinter import *
import matplotlib.pyplot as plt

class MainFrame(Tk):
    def __init__(self, parent):
        self._parent =  parent
        self.initialize()
        welf._projectname = None
        return

    def initialize(self):
        w, h = self.maxsize()
        self.geometry('%dx%d' % (w,h))
#        self.mainframe = Frame(self, background="bisque")
#        self.mainframe.pack(side="top", fill="both", expand=True)
#        self.leftframe = Frame(self, background="bisque")
#        self.leftframe.pack(side="left", fill='x', expand=True)
#        self.rightframe = Frame(self, background="blue")
#        self.rightframe.pack(side="right", fill='x', expand=True)
        return

if __name__ == '__main__':
    app = MainFrame(None)
    app.title('Pyquan')
    app.mainloop()
