
import sys
import os 
script="/global/scratch/users/siennaw/scripts/HRRRpy"
if script not in sys.path: # Add the current directory to the Python path
    sys.path.append(script)
from HRRR_lib import HRRR 
import xarray as xr
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

ds = xr.open_dataset(fn)
print(ds)
# AQS Data
#dfn ='/global/home/users/siennaw/scratch/data/obs/aqs/source/dat/AQS_%s.dat' % date 
# dfn = '/global/scratch/users/siennaw/data/obs/aqs/source/dat/AQS_%s.dat' % date 
dfn = "/global/scratch/users/rasugrue/convert2bufr/dat_vNov2024/PA_%s.dat" % date
hrrr = HRRR(fn)
hrrr.set_date(date)
hrrr.plot_variable_with_data(data_fn = dfn, before = False, vmax = 100)
hrrr.plot_variable_with_data(data_fn = dfn, before = True, vmax = 100)
hrrr.plot_comparison(vmax = 100) 




# hrrr = HRRR(fn)


# dfn ='/global/home/users/siennaw/scratch/data/obs/aqs/source/dat/AQS_2018111400.dat'


# hrrr.plot_variable_with_data(data_fn = dfn, before = True, vmax = 200)
