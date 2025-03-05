
print("Running temp0.py")
import xarray as xr
# import pandas as pd 
# import os

print("Running temp1.py")
# ~/.conda/envs/smoke_env/bin/python
fn = "/global/scratch/users/siennaw/gsi_2024/grib2nc/2019/working/2019121121/met_em.d01.2019-12-11_23:00:00.nc"
# fn = "/global/scratch/users/siennaw/gsi_2024/convert_grib2nc/wps_files/blank_wrfinput.nc" 
fn = "/global/scratch/users/siennaw/gsi_2024/grib2nc/2019/working/2019121121/met_em.d01.2019-12-11_21:00:00.nc"
# fn = "/global/scratch/users/siennaw/gsi_2024/grib2nc/working/2020010109/met_em.d01.2020-01-01_11:00:00.nc"
# fn = "/global/scratch/users/siennaw/gsi_2024/runs/run_105/wrf_inout_2018110806"
data = xr.open_dataset(fn)
# data = data.drop_vars(["PM2_5_DRY_INIT", "PM2_5_DRY"])
print(data.Time)
print(data.Times.values)
# for i in data.attrs:
#     print(i, data.attrs[i])
# print(data.attrs)

assert(False)
print(data['MASSDEN'])

print(data)
# data.to_netcdf("/global/scratch/users/siennaw/gsi_2024/run_gsi/input_files/wrfinput4run")
assert(False)
# print(data.Time.values)



directory = "/global/scratch/users/siennaw/gsi_2024/output/101"
# Get list of files in directory
files = os.listdir(directory)
files.remove("convinfo")
files.remove("gsiparm.anl")
files = sorted(files)
files = files[0:24]

dates = [filename.replace("wrf_inout_","") for filename in files]
times = pd.to_datetime(dates, format='%Y%m%d%H')

def prep_df(dataset, time):
    dataset = dataset.isel(Time=0).isel(bottom_top=0)
    dataset = dataset[['PM2_5_DRY_INIT', 'PM2_5_DRY']]
    dataset = dataset.assign_coords(Time=time)
    return dataset

# Get first file
i = 0
data = xr.open_dataset("%s/wrf_inout_%s" % (directory, dates[i]))
dataout = prep_df(data, times[i])
dataout.to_netcdf("test.nc")

for i in range(1, len(files)):
    print("On file %d/%d" % (i, len(files)))
    data = xr.open_dataset("%s/wrf_inout_%s" % (directory, dates[i]))
    data = prep_df(data, times[i])
    dataout = xr.concat([dataout, data], dim='Time')
print(dataout)
dataout.to_netcdf("test.nc")
