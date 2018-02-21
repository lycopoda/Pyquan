import cProfile, pstats, io
import check_peak
pr = cProfile.Profile()
pr.enable()
check_peak.main()
pr.disable()
s=io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
