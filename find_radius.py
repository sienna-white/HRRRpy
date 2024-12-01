import xarray as xr
import numpy as np 

def find_change(ds):
    var_before = ds['PM2_5_DRY_INIT'].isel(bottom_top=0).isel(Time=0)
    var_after = ds['PM2_5_DRY'].isel(bottom_top=0).isel(Time=0)
    difference = var_after - var_before
    total_change = abs(difference) > 1e-5
    number_of_cells = sum(sum((total_change)))
    return number_of_cells.values

def calculate_radius(n):
    area_of_cell = 9 
    area = area_of_cell * n 
    radius = np.sqrt(area/np.pi)
    return radius 



data201 = xr.open_dataset('/global/scratch/users/siennaw/gsi_2024/runs/run_201/wrf_inout_2018111912')
data202 = xr.open_dataset('/global/scratch/users/siennaw/gsi_2024/runs/run_202/wrf_inout_2018111912')
data203 = xr.open_dataset('/global/scratch/users/siennaw/gsi_2024/runs/run_203/wrf_inout_2018111912')
data204 = xr.open_dataset('/global/scratch/users/siennaw/gsi_2024/runs/run_204/wrf_inout_2018111912')

data205 = xr.open_dataset('/global/scratch/users/siennaw/gsi_2024/runs/run_205/wrf_inout_2018111912')
data206 = xr.open_dataset('/global/scratch/users/siennaw/gsi_2024/runs/run_206/wrf_inout_2018111912')
data207 = xr.open_dataset('/global/scratch/users/siennaw/gsi_2024/runs/run_207/wrf_inout_2018111912')
data208 = xr.open_dataset('/global/scratch/users/siennaw/gsi_2024/runs/run_208/wrf_inout_2018111912')


r = calculate_radius(find_change(data201))
print("The radius for run 201 is %d km^2" % r)

r = calculate_radius(find_change(data202))
print("The radius for run 202 is %d km^2" % r)

r = calculate_radius(find_change(data203))
print("The radius for run 203 is %d km^2" % r)

r = calculate_radius(find_change(data204))
print("The radius for run 204 is %d km^2" % r)

r = calculate_radius(find_change(data205))
print("The radius for run 205 is %d km^2" % r)

r = calculate_radius(find_change(data206))
print("The radius for run 206 is %d km^2" % r)

r = calculate_radius(find_change(data207))
print("The radius for run 207 is %d km^2" % r)

r = calculate_radius(find_change(data208))
print("The radius for run 208 is %d km^2" % r)