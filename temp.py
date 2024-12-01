import xarray as xr
import pandas as pd 

data = xr.open_dataset("/global/scratch/users/siennaw/gsi_2024/output/101/wrf_inout_2018110808")
# print(data.data_vars)
data = data.isel(Time=0)
print(data)

dataout = data[['PM2_5_DRY_INIT', 'PM2_5_DRY']]
time = "2018110808"
time = pd.to_datetime(time, format='%Y%m%d%H')
print(time)
dataout = dataout.assign_coords(Time=time)
print(dataout)

dataout.to_netcdf("test.nc")
