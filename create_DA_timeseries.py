import sys
import os 
if os.getcwd() not in sys.path: # Add the current directory to the Python path
    sys.path.append(os.getcwd())
from pyproj import Proj, transform, Transformer
import matplotlib.pyplot as plt
from HRRR_lib import HRRR 
import pandas as pd 
import re 
import pandas as pd 
import numpy as np 
import xarray as xr 
from haversine import haversine_vector, Unit
import matplotlib.dates as mdates 
hours = mdates.HourLocator(interval = 48)  #
h_fmt = mdates.DateFormatter('%m/%d')

# ~/.conda/envs/smoke_env/bin/python

times = pd.date_range("Nov 08 2018 06:00", "Nov 20 2018 23:00", freq='1h')

# ******************************* HRRR SMOKE ***********************************
fn ="/global/scratch/users/siennaw/gsi_2024/output/101/wrf_inout_2018111101"
hrrr = HRRR(fn)
mlon, mlat = hrrr.lons.values, hrrr.lats.values

# ************************** PURPLE AIR DATA ***********************************
pa = "/global/scratch/users/rasugrue/data/PA_data/PA_data_monthly_QAQC_out2/PA_11_2018.csv" 
pdata = pd.read_csv(pa, low_memory=False)
pdates = pd.to_datetime(pdata.time_GMT)
pdata['dates'] = pdates 
pval = pdata['PM2.5_CORRECTED'].values 
plat = pdata['PA_Latitude'].values
plon = pdata['PA_Longitude'].values
print("Finished reading in Purple Air data (%d datapoints)" % len(pval))

# 06, 4610, 4613, 4615, 12811, 4621, 12825, 12839, 4658, 4660, 12853, 4662, 12857, 4666, 12865, 4676, 12869, 12873, 4682, 4686, 4694, 4698, 4702, 4704, 4708, 4719, 4721, 4725, 4727, 4734, 4736, 12929, 12931, 4740, 4742, 4744, 12939, 12945, 4758, 12951, 4762, 12955, 4766, 4770, 12967, 12971, 12975, 4788, 4793, 4797, 4801, 4805, 4817, 13015, 4825, 13021, 13023, 13039, 4850, 13073, 13077, 4896, 4904, 4907, 13115, 13119, 4928, 4930, 4952, 13165, 4974, 4980, 13173, 13175, 13183, 13187, 13189, 13191, 13193, 13201, 13207, 5016, 5030, 13249, 13265, 13269, 5084, 13287, 13291, 13303, 5127, 13325, 13327, 5151, 5184, 5218, 5222, 5228, 5252, 5254, 5264, 5292, 13511, 13513, 13517, 13519, 13523, 5432, 5436, 5488, 5492, 5500, 5504, 5510, 5574, 5586, 5642, 5650, 13907, 13929, 5744, 13961, 5776, 5778, 5782, 13989, 5798, 
# print(set(pdata['SENSOR_INDEX']))
sites = [ 4896, 4904, 4907,]
nsites = 1

fig, axs = plt.subplots(figsize=(10,7), nrows=len(sites), ncols=1, sharex=True, sharey=True)


# From WGS84 to UTM Zone 10 (ESPG:32610)
transform0 = Transformer.from_crs(4326, 32610)

lats = mlat.ravel()
lons = mlon.ravel()
mx, my = transform0.transform(lats, lons)

file = 102
    
def ind4site(pa_lat, pa_lon):
    # print("\t Calculating the haversine_vector...")
    shape0 = mlon.shape

    pax, pay = transform0.transform(pa_lat, pa_lon)
    distance = (pax - mx)**2 + (pay - my)**2

    # distance = haversine_np(lons, lats, pa_lon, pa_lat)
    # print(distance)
    index = (distance < (3000)**2)  # Find indicies of overlap 
    # print(np.min(distance))
    print(lats[index], lons[index])
    # print(lats[index].shape)
    print(pa_lat, pa_lon)
    # assert(False)
    index = np.reshape(index, shape0)

    return index 



site_dict = {} 
model_data_before = {}
model_data_after = {} 


for s,site in enumerate(sites):
    print("Calculating index for site %s" % site)
    data_at_site = pdata.loc[pdata['SENSOR_INDEX'] == site]
    pa_lat, pa_lon = data_at_site['PA_Latitude'].values[0], data_at_site['PA_Longitude'].values[0]
    index = ind4site(pa_lat, pa_lon)
    site_dict[site] = index 
    model_data_before[site]  = np.zeros((len(times),))
    model_data_after[site]  = np.zeros((len(times),))

    axs[s].plot(data_at_site.dates, data_at_site['PM2.5_CORRECTED'],'-o', color="#3da5d9", label="Purple Air data @ sensor %d" % site) 


for t,time in enumerate(times):
    print('\t', time)
    year = time.year
    month = time.month
    day = time.day
    hour = time.hour
    date4file = time.strftime("%Y%m%d%H")

    try:
        fn ="/global/scratch/users/siennaw/gsi_2024/output/%d/wrf_inout_%s" % (file, date4file) 
        hrrr = xr.open_dataset(fn)
    except:
        print("Couldn't find file %s" % date4file)
        continue 

    for s,site in enumerate(sites):

        index = site_dict[site]
        
        # Smoke data before assimilation 
        smoke_before = hrrr['PM2_5_DRY_INIT'].isel(bottom_top=0).isel(Time=0).values[index]
        smoke_before = np.squeeze(smoke_before)

        # Smoke data after assimilation 
        smoke_after = hrrr['PM2_5_DRY'].isel(bottom_top=0).isel(Time=0).values[index]
        smoke_after = np.squeeze(smoke_after)

        model_data_after[site][t] = np.mean(smoke_after)
        model_data_before[site][t] = np.mean(smoke_before)



for s,site in enumerate(sites):
    axs[s].plot(times, model_data_after[site],'-', color="#fec601", linewidth=3, label="After assimilation")
    axs[s].plot(times, model_data_before[site], '-',  color="#ea7317", linewidth=3, label="Before assimilation")
    axs[s].set_xlim(times[0], times[-1])
    axs[s].set_ylim(0, 250)
    axs[s].grid(alpha=0.5)
    axs[s].xaxis.set_major_locator(hours)
    axs[s].xaxis.set_major_formatter(h_fmt)
    axs[s].legend(fontsize=11)
    axs[0].set_title("%s" % times[0].strftime("%d %m %Y"))


fig.savefig("Nov8-20_%d.png" % file)
assert(False)

