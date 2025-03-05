import sys
import os 
if os.getcwd() not in sys.path: # Add the current directory to the Python path
    sys.path.append(os.getcwd())
from pyproj import Proj, transform, Transformer
from HRRR_lib import HRRR 
import pandas as pd 
import numpy as np 
import xarray as xr 
import matplotlib.pyplot as plt


# ~/.conda/envs/smoke_env/bin/python

# ******************************* HRRR SMOKE ***********************************
fn ="/global/scratch/users/siennaw/gsi_2024/output/101/wrf_inout_2018111101"
hrrr = HRRR(fn)
mlon, mlat = hrrr.lons.values, hrrr.lats.values

# From WGS84 to UTM Zone 10 (ESPG:32610)
transform0 = Transformer.from_crs(4326, 32610)

# Unroll to 1D vectors. Save original dims of the grid.
shape = mlat.shape
lats = mlat.ravel()
lons = mlon.ravel()

plt.plot(lons, lats, '.')
fig = plt.gcf()
fig.savefig("test0.png")

# mx, my = transform0.transform(lats, lons)
mx, my = transform0.transform(lats, lons)

# Create output CSV 
data_out= pd.DataFrame()
data_out["model_lat"] = lats
data_out["model_lon"] = lons
data_out["model_utmx"] = mx
data_out["model_utmy"] = my

data_out_fn = "HRRRgrid.csv"
with open(data_out_fn, 'w') as file:
    file.write('HRRR-Smoke CA grid saved with lat,lon (ESPG:4326) and UTM (ESPG:32610). Data shape is (%d, %d).\n' % shape)
    data_out.to_csv(file, header=True, index=False)


# plt.plot(mx, my, '.')
# fig = plt.gcf()
# fig.savefig("test.png")