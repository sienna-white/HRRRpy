
import sys
import os 
if os.getcwd() not in sys.path: # Add the current directory to the Python path
    sys.path.append(os.getcwd())
from HRRR_lib import HRRR 
import pandas as pd 
import re 

try:
    fn = sys.argv[1]
except:
    Exception('No filepath passed to function!')

try:
    date = sys.argv[2]
except:
    print('No date string passed to function!')

print('fn = %s' % fn)
print('Date = %s' % date)

# AQS Data
dfn ='/global/home/users/siennaw/scratch/data/obs/aqs/source/dat/AQS_%s.dat' % date 

hrrr = HRRR(fn)
hrrr.plot_variable_with_data(data_fn = dfn, before = True, vmax = 200)
hrrr.plot_variable_with_data(data_fn = dfn, before = False, vmax = 200)
hrrr.plot_comparison(vmax = 200) 




# hrrr = HRRR(fn)


# dfn ='/global/home/users/siennaw/scratch/data/obs/aqs/source/dat/AQS_2018111400.dat'


# hrrr.plot_variable_with_data(data_fn = dfn, before = True, vmax = 200)