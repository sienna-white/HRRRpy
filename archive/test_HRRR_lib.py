import os 
import sys
if os.getcwd() not in sys.path: # Add the current directory to the Python path
    sys.path.append(current_directory)
from HRRR_lib import HRRR 
import pandas as pd 

# fn = '/global/scratch/users/siennaw/data/wrf/wrfinput_d01_2018111400.nc'
# hrrr = HRRR(fn)
# print(hrrr.get_extent())
# ds = hrrr.get_ds() 
# print(ds.data_vars)
# # hrrr.plot_var(var='PM2_5_DRY', vmin=0)

dfn ='/global/home/users/siennaw/scratch/data/obs/aqs/source/dat/AQS_2018111400.dat'
aqs_data = pd.read_csv(dfn,  delim_whitespace=True) #, header=None, names=['siteID', 'PM2.5', 'latitude', 'longitude', 'time', 'days', 'elevation', 'measured'])
print(aqs_data)

# hrrr.plot_variable_with_data(data_fn = dfn, before = True, vmax = 200)
