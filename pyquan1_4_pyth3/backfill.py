import sys

def bf(RTdict, CFdict, library, threshold=3):
    RTlist = make_RTlist (RTdict, threshold)
    for code in RTlist:
        RT_lib = library.RT(code)
        for sample in RTdict:
            CF = CFdict[sample]
            if not code in sample:
                RTdict[sample][code] = ((RT_lib - CF[1]) / CF[0], 0)
    return RTdict

def make_RTlist(RTdict, threshold):
    RT_count = {}
    RT_list = []
    for sample in RTdict:
        for code in RTdict[sample]:
            RT_count[code] = RT_count.setdefault(code, 0) + 1
    for i in RT_count:
        if threshold < RT_count[i] <len(RTdict):
            RT_list.append(i)
    return RT_list
            
