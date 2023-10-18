import os 
import sys
if os.getcwd() not in sys.path: # Add the current directory to the Python path
    sys.path.append(current_directory)
from HRRR_lib import HRRR 


fn = '/global/home/users/siennaw/scratch/GSI/runs/test7/wrf_inout'

hrrr = HRRR(fn)


hrrr.plot_var(var='PM2_5_DRY', vmin=0)