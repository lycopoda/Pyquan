import matplotlib.pyplot as plt

class Plot(object):
    def __init__(self):
        plt.figure()
        plt.xlabel('Time (min)')
        plt.ylabel('intensity')

    def __enter__(self):
        return

    def __exit__(self, type, value, traceback):
        plt.close()
        return
