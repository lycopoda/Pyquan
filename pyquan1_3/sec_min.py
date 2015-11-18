def sec_min(time):
    minutes = int(time)/60
    seconds = int(time - minutes*60)
    return '{0}min{1}s'.format(minutes, seconds)
