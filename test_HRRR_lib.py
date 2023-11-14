import os 
import sys
if os.getcwd() not in sys.path: # Add the current directory to the Python path
    sys.path.append(current_directory)
from HRRR_lib import HRRR 
import pandas as pd 

# fn = '/global/home/users/siennaw/scratch/tmp/data/bkg/grib2wrf/2018111118/wrfinput_d01_2018-11-11_19:00:00.nc'
fn = '/global/home/users/siennaw/scratch/data/wrf/wrfinput_d01_2018111400.nc'
hrrr = HRRR(fn)

# ds = hrrr.get_ds() 
# print(ds.data_vars)
# # hrrr.plot_var(var='PM2_5_DRY', vmin=0)

dfn ='/global/home/users/siennaw/scratch/data/obs/aqs/source/dat/AQS_2018111400.dat'


hrrr.plot_variable_with_data(data_fn = dfn, before = True, vmax = 200)
