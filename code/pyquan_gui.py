#!/usr/bin/python

import os, sys, calibrate, quantify, normalize, analyse
from tkinter import *
import matplotlib.pyplot as plt

'''
In main menu, project -> select project -> project window will be opened.
Project window: 
    left: analysis buttons, information text screen, button to select parameter data
    (total or peak), parameterbox
    right: Buttons to select project or peak parameters, button to update peak
    parametersm, based on project values.
    right: choose for TIC (with peak data if present (or select specific
    masses), calibration or individual peaks (At bottom of graphs back and
    forth or to next peak)
'''

class MakeButton(object):
    def __init__(self, root):
        self._root = root

    def button(self, name, command):
        b = Button(self._root, text=name, command=command)
        b.pack(side='left')
        return b



class Pyquan(Tk):
    def __init__(self, parent):
        Tk.__init__(self, parent)
        w, h = self.maxsize()
        self.geometry('%dx%d' % (w,h))
        self.mainmenu()
        
    def projectmenu(self):
        projectmenu = Menu(self._menu)
        self._menu.add_cascade(label='Project', menu=projectmenu)
        chooseprojectmenu = Menu(self._menu)
        projectmenu.add_cascade(label='Choose project',
                                menu=chooseprojectmenu)
        projectlist = self.projectlist()
        for name in projectlist:
            chooseprojectmenu.add_radiobutton(label=name, 
                        indicatoron=0,
                        value=name,
                        command=lambda arg0=name: self.new_project(arg0))
        projectmenu.add_command(label = 'Exit', command=self.quit)
        return

    def mainmenu(self):
        self._menu = Menu(self)
        self.config(menu=self._menu)
        self.projectmenu()
        return

    def new_project(self, name):
        project = Toplevel(self)
#        project.title = name
        project.pack(side='top', fill='both', expand=True, background='green')
#        self.leftframe =  Frame(project, background='bisque')
#        self.leftframe.pack(side='left', fill='both', expand=True)
#        self.leftbuttons = Frame(project.leftframe, background='yellow')
#        self.leftbuttons.pack(side='top', fill='x', expand=False)
#        self.analysis_buttons()
#        self.infoframe = Frame(self.leftframe, background='blue')
#        self.infoframe.pack(side='top', fill='x', expand=False)
#        self.textbox()
#        self.leftbottom =  Frame(self.leftframe, background='green')
#        self.leftbottom.pack(side='bottom', fill='both', expand=True)
#        self.rightframe = Frame(self, background='blue')
#        self.rightframe.pack(side='right', fill='both', expand=True)
#        self.rightbuttons = Frame(self.rightframe, background='yellow')
#        self.rightbuttons.pack(side='top', fill='x', expand=False)
#        self.graphics_buttons()
#        self._projectname = None
        return

    def analysis_buttons(self):
        b = MakeButton(self.leftbuttons)
        project = b.button('project', self.show_projects)
        analyse =  b.button('analyse all', self.analyse)
        calibrate = b.button('calibrate', self.calibrate)
        normalize = b.button('normalize', self.normalize)

    def show_projects(self):
        return

    def analysis(self):
        return

    def calibrate(self):
        return

    def quantify(self):
        return

    def normalize(self):
        return

    def graphics_buttons(self):
        b = MakeButton(self.rightbuttons)
        calibrate = b.button('calibration', self.calibration)
        analyse =  b.button('quantification', self.quantification)
        normalize = b.button('normalization', self.normalization)

    def calibration(self):
        return

    def quantification(self):
        return

    def normalization(self):
        return

    def initialize(self):
        self.mainmenu()
        
        self.grid()
        analysis_ = Canvas(self, height=200)
        analysis_canvas.grid(column=0, row=0)
        self._textbox = Text(self, height=5, width=50, spacing3=5)
        self._textbox.grid(column=0,row=1)
        self.textbox()
        buttoncanvas = Canvas(self, height=100)
        buttoncanvas.grid(column=1, row=0)
        graphics_canvas = Canvas(self)
        graphics_canvas.grid(column=1, row=2, rowspan=2)
        self.buttons(buttoncanvas)
        pass


    def framework(self):
        ctextbox = Canvas(self).grid()
        self.textbox(ctextbox)
        cbuttons = Canvas(self).grid(column=0, row=1)
        self.buttons(cbuttons)
        cparam_project = Canvas(self).grid(column=0,row=2,rowspan=3)
        cparam_peak = Canvas(self).grid(column=0,row=5,rowspan=3)
        cgraphs = Canvas(self).grid(column=1, row=0, columnspan=2,rowspan=8)
        self.graphs(cgraphs)
        return

    def graphs(self, cgraphs):
        self.fig = plt.figure()

        return

    def textbox(self):
        self.infotext = Text(self.infoframe, width=50, height=5, spacing3=5)
        self.infotext.pack(side='top', fill='both', expand=False)
        self.infotext.tag_configure('bold', font=('ubuntu', 12, 'bold'))
        self.infotext.tag_configure('normal', font=('ubuntu', 12))
        self.infotext.tag_configure('red', foreground='red', font=('ubuntu',
        12))
        self.infotext.tag_configure('green', foreground='forest green',
        font=('ubuntu', 12))
        self.infotext.insert(1.0, '\nProject: No project selected\n', 'normal')
        return

    def textbox_old(self):
        self._textbox.tag_configure('bold', font=('ubuntu', 12, 'bold'))
        self._textbox.tag_configure('normal', font=('ubuntu', 12))
        self._textbox.tag_configure('red', foreground='red', font=('ubuntu', 12))
        self._textbox.tag_configure('green', foreground='forest green', font=('ubuntu', 12))
        self._textbox.insert(1.0, '\nProject: No project selected\n', 'normal')
        return

    def buttons(self, cbuttons):
        cal=Button(cbuttons,text='Calibration', command=self.showcal)
        cal.grid(row=0, column=0)
        quant = Button(cbuttons, text='Quantification',command=self.showquant)\
        .grid(row=0,column=1,)
        norm = Button(cbuttons,
        text='Normalization',command=self.shownorm).grid(row=0,column=2)
        return

    def showcal(self):
        '''Show callibration graphs'''
        return

    def showquant(self):
        '''Show callibration graphs'''
        return

    def shownorm(self):
        '''Show callibration graphs'''
        return

    def projectlist(self):
        projectdir = os.path.join('..', 'projects')
        projectset = set()
        for item in os.listdir(projectdir):
            if os.path.isdir(os.path.join(projectdir, item)):
                projectset.add(item)
            elif item.endswith('.txt'):
                projectset.add(item[:-4])
        return sorted(projectset)

        
    def analysemenu(self):
        analysemenu = Menu(self._menu)
        self._menu.add_cascade(label='Analyse', menu=analysemenu)
        analysemenu.add_command(label='Complete', 
                                command=self.analyse)
        analysemenu.add_command(label='Calibrate',
                                command=Calibrate(self).process)
        analysemenu.add_command(label='Quantify',
                                command=self.quantify)
        analysemenu.add_command(label='Normalize',
                                command=self.normalize)
        return

    def analyse(self):
        self.calibrate()
        self.quantify()
        self.normalize()
        return

    def calibrate(self):
        Calibrate(self).process()
        self_button_cal.ACTIVE
        return

    def quantify(self):
        Quantify(self).process()
        return

    def normalize(self):
        if self._projectname:
            Normalize(self).process()
        return


class Calibrate(object):
    def __init__(self, root):
        self._r = root
        self._p = ("Calibrate", calibrate.main)

    def process(self):
        self._r._textbox.delete(3.0, END)
        self._r._textbox.insert(END, '\n{0}'.format(self._p[0]), 'normal')
        self._r._textbox.insert(END, '\tprocessing', 'red')
        self._r.config(cursor='circle')
        self._r.update()
        if self._r._projectname:
            self._p[1](self._r._projectname)
        self._r._textbox.delete(3.0, END)
        self._r._textbox.insert(END, '\n{0}'.format(self._p[0]), 'normal')
        self._r._textbox.insert(END, '\tfinished', 'green')
        #create window to check calibrations
        self.plots
        self._r.config(cursor='')
        self._r.update()
        return
        
    def plots(self):
        #create list of plot names
        calframe = Frame(height=2, bd=1)
        #create previous, next, save and close buttons
        #open first plot
        calframe.pack(fill=X, padx=5, pady=5)
        return

class Quantify(Calibrate):
    def __init__(self, root):
        self._r = root
        self._p = ('Quantify', quantify.main)

class Normalize(Calibrate):
    def __init__(self, root):
        self._r = root
        self._p = ('Normalize', normalize.main)



if __name__ == '__main__':
    app = Pyquan(None)
    app.title('Pyquan')
    app.mainloop()

