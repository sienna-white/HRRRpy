import sys
import os 
if os.getcwd() not in sys.path: # Add the current directory to the Python path
    sys.path.append(os.getcwd())


from HRRR_lib import HRRR 
import pandas as pd 
import re 
import pandas as pd 
import numpy as np 


date = "2018110808"


year = date[0:4]
month = date[4:6]
day = date[6:8]
hour = date[8:10]
datetime = pd.to_datetime("%s/%s/%s %s:00" % (month,day,year,hour)) 

# ************************** PURPLE AIR DATA ***********************************
pa = "/global/scratch/users/rasugrue/data/PA_data/PA_data_monthly_QAQC_out2/PA_11_2018.csv" 
pdata = pd.read_csv(pa)
pdates = pd.to_datetime(pdata.time_GMT)
pdata = pdata.loc[pdates == datetime].reset_index(drop=True)

pval = pdata['PM2.5_CORRECTED'].values 
plat = pdata['PA_Latitude'].values
plon = pdata['PA_Longitude'].values
print("Finished reading in Purple Air data (%d datapoints)" % len(pval))

# ******************************* HRRR SMOKE ***********************************
fn ="/global/scratch/users/siennaw/gsi_2024/test_run/wrf_inout_2018110808"
hrrr = HRRR(fn)
mlon, mlat = hrrr.lons.values, hrrr.lats.values

# Smoke data before assimilation 
smoke_before = hrrr.ds['PM2_5_DRY_INIT'].isel(bottom_top=0).isel(Time=0).values
smoke_before = np.squeeze(smoke_before)

# Smoke data after assimilation 
smoke_after = hrrr.ds['PM2_5_DRY'].isel(bottom_top=0).isel(Time=0).values
smoke_after = np.squeeze(smoke_after)

# ******************************* AQS DATA ***********************************
afn ='/global/scratch/users/siennaw/data/obs/aqs/source/dat/AQS_%s.dat' % date
adata = pd.read_csv(afn) 
alon, alat, aval = adata.longitude, adata.latitude, adata['PM2.5']
alon = alon - 360
print("Finished reading in AQS data (%d datapoints)" % len(aval))

# ******************************* COMPARE AQS DATA ***********************************
aqs_data_scatter_before = np.zeros((len(alon),2))
aqs_data_scatter_after  = np.zeros((len(alon),2))

for i, (la,lo) in enumerate(zip(alat, alon)):
    
    distance = (mlon - lo)**2 + (mlat - la)**2 
    index = (distance< 0.03)  # Find indicies of overlap 
    aqs_data_scatter_before[i,0] = aval[i]
    aqs_data_scatter_before[i,1] = np.mean(smoke_before[index])

    aqs_data_scatter_after[i,0] = aval[i]
    aqs_data_scatter_after[i,1] = np.mean(smoke_after[index])

# ******************************* COMPARE PURPLE AIR DATA ***********************************
pa_data_scatter_before = np.zeros((len(plon),2))
pa_data_scatter_after  = np.zeros((len(plon),2))

for i, (la,lo) in enumerate(zip(plat, plon)):
    
    distance = (mlon - lo)**2 + (mlat - la)**2 
    index = (distance< 0.03)  # Find indicies of overlap 
    pa_data_scatter_before[i,0] = pval[i]
    pa_data_scatter_before[i,1] = np.mean(smoke_before[index])

    pa_data_scatter_after[i,0] = pval[i]
    pa_data_scatter_after[i,1] = np.mean(smoke_after[index])



import matplotlib.pyplot as plt

fig = plt.figure()
ax = plt.gca() 
ax.set_xlim(0,50)
ax.set_ylim(0,50)
ax.plot(aqs_data_scatter_before[:,0], aqs_data_scatter_before[:,1], '.', markersize=20, alpha=0.6, color="#7d923a")
ax.plot(aqs_data_scatter_after[:,0], aqs_data_scatter_after[:,1], '.', markersize=20, alpha=0.6, color="#674ea7")

ax.plot(pa_data_scatter_before[:,0], pa_data_scatter_before[:,1], '^', markersize=10, alpha=0.6, color="#7d923a")
ax.plot(pa_data_scatter_after[:,0], pa_data_scatter_after[:,1], '^', markersize=10, alpha=0.6, color="#674ea7")
ax.grid(alpha=0.5)

ax.plot([],[], '.', markersize=20, alpha=0.6, color="#7d923a", label="AQS:Model before assimilation")
ax.plot([],[], '.', markersize=20, alpha=0.6, color="#674ea7", label="AQS:Model after assimilation")
ax.plot([],[], '^', markersize=10, alpha=0.6, color="#7d923a", label="PA:Model before assimilation")
ax.plot([],[], '^', markersize=10, alpha=0.6, color="#674ea7", label="PA:Model after assimilation")

ax.set_xlabel("Observed data")
ax.set_ylabel("Model data")
ax.legend()
fig.savefig("scatter.png")

# Read in purple air data 


#   cp /global/scratch/users/tinakc/PA_bufr_data_5percentNov/HourlyPM_${date}.bufr ./pm25bufr_pa
#   cp /global/scratch/users/siennaw/data/obs/aqs/bufr/HourlyPM_${date}.bufr pm25bufr2