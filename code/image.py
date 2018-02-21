'''This module show plots of the peaks, in black the original intensity data,
in red the estimated peak of interest (either the fitted function, or part of
the real data, and in blue the overlapping peaks (if present).'''
import os, sys
from peak_fit import Fit
from matplotlib import pyplot as plt
from argparse import ArgumentParser
import numpy as np
import h5py

def image():
    data=h5py.File(file_name, 'r')
    peak_dict = {}
    for sample in data:
        for code in data[sample]:
            if code in data[sample]:
                peak = data[sample][code]
                peak_dict[sample] = (peak['x'], peak['y'])
    plots = []
    for sample in peak_dict:
        x,y = peak_dict[sample]
        plots.append(peak_dict[sample])

    curr_pos = 0
def key_event(e):
    global curr_pos
    if e.key == 'right':
        curr_pos += 1
    elif e.key == 'left':
        curr_pos -= 1
    elif e.key == 'd':
        ax.cla()
        #delete peak from data file
        #update peak list
    elif e.key == 'D':
        ax.cla()
        #delete peak from all samples in data file
        #update peak list
    elif e.key =='c':
        #update and open check_peak init file
        #save init file
        e.key =='c':
            #run check_peak
            #update peak list
            #open at same peak
    else:
        plt.close()
        return
    curr_poss = curr_pos % len(plots)
    ax.cla()
    x,y = plots[curr_poss]
    ax.plot(x,y)
    fig.canvas.draw()

def image_plot():
    fig = plt.figure()
    fig.canvas.mpl_connect('key_press_event', key_event)
    ax = fig.add_subplot(111)
    x,y = plots[0]
    ax.plot(x,y)
    plt.plot(x,y)
    plt.show()

class Plot(object):
    def __init__(self, project

class PeakList(object):
    def __init__(self, project):
        self._project = project
        self.create_list()

    def create_list(self):
        self._peak_list = []
        with open(self._project.path.hdf5, 'r') as data:
            for code in self._project.library:
                for sample in self._project.runlist:
                    self._peak_list.append((sample, code))
        return

    def peak(self, idx):
        return self._peak_list[idx]

    def peak_idx(self, code, sample):
        try:
            return self._peak_list.index((sample, code))
        except ValueError:
            return None

def get_info():
    arg_parser = ArgumentParser(description = 'Image peaks')
    arg_parser.add_argument('project_name', metavar='project name', type=str,
    help='The project name')
    return arg_parser.parse_args().project_name

def main(project_name=None, sample=None, code=None):
    if not project_name:
        project_name = get_info()
    project = project.Project(project_name)
    #create peak list, ordered by library RT and sample list
    peak_list = PeakList(project_name)
    #search for memory file; if present, get index of code and sample
    #otherwise, give first sample and code
    plot = Plot(project, sample, code)
    plots.image()
    return 0

if __name__=='__main__':
    status = main()
    sys.exit(status)
