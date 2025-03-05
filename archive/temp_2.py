
import xarray as xr 


filename = "/global/scratch/users/siennaw/gsi_2024/output/PROCESSED_PARAM_6/wrf_inout_2017112606"
data = xr.open_dataset(filename)

surface_layer_before = data["PM2_5_DRY_INIT"].isel(bottom_top=0).isel(Time=0)
surface_layer_after = data["PM2_5_DRY"].isel(bottom_top=0).isel(Time=0)



print(surface_layer_after.shape)

print(surface_layer_after)


import matplotlib.pyplot as plt

fig = plt.figure(figsize=(10, 10))
plt.plot(surface_layer_before, surface_layer_after, 'o', color="black")
ax = plt.gca()
ax.grid(True)
fig.savefig("test.png")



