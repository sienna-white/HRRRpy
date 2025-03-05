import pandas as pd 
from pyproj import Proj, transform, Transformer
import numpy as np 
import xarray as xr 
import time as timing 


import sys 
# Get arguement if running in slurm 
if len(sys.argv) > 1:
    file = int(sys.argv[1])
# Otherwise just hardcode it:
# file = 101


print("Running for file %d" % file) 

start_date = '2019100100'   # Starting date for the files we want to look at 
ndays = 30                # Number of days to look at
 

# *** Functions ***
def to_file_date(datetime_obj):
   return time.strftime("%Y%m%d%H")  
tasks = []

# *********************************************************************
start_date_dt = pd.to_datetime(start_date, format="%Y%m%d%H")
end_date_dt = start_date_dt + pd.Timedelta(days=ndays)
times = pd.date_range(start_date_dt, end_date_dt, freq="1h")
# *********************************************************************

### Parse month, date, year
assert(end_date_dt.month == start_date_dt.month ) # script can't handle multiple months rn 
month = start_date_dt.month 
year = start_date_dt.year 
# *********************************************************************

# Load the entire Purple Air dataset once
pa_data_path = '/global/scratch/users/rasugrue/convert2bufr/validation_vNov2024/validation_data_%d_%d.csv' % (month, year)
df_pa = pd.read_csv(pa_data_path)
df_pa['times'] = pd.to_datetime(df_pa['DATA_TIME_STAMP'])                       # convert to datetime 
print("Loaded Purple Air data successfully. Number of entries:", len(df_pa)) 

# Save some memory by cropping to just relevant columns
df_pa = df_pa[['siteID', 'TEMPERATURE_A', 'TEMPERATURE_B', 'PM2_5_ATM_A',
       'PM2_5_ATM_B', 'PM2_5_CF_1_A', 'PM2_5_CF_1_B', 'PM2.5', 
       'PM2.5_CORRECTED', 'Site Num', 'times']]
# *********************************************************************

# Crop PA dataset to just rows in our time range  
df_pa = df_pa[(df_pa['times'] >= start_date_dt) & (df_pa['times'] <= end_date_dt)]
print("Cropped Purple Air data successfully. Number of entries:", len(df_pa))

# Crop out site 7174
df_pa = df_pa[df_pa['siteID'] != 7174]
print("Cropped Purple Air data successfully. Number of entries:", len(df_pa))
# *********************************************************************

# Create a dataframe to store the comparison data
COMPARE = pd.DataFrame()
COMPARE["sensor"] = df_pa["siteID"]
COMPARE["time"] = df_pa["times"]
COMPARE["pm25_PA"] = df_pa["PM2.5_CORRECTED"]
COMPARE["model_before_da"] = np.nan
COMPARE["model_after_da"] = np.nan
# *********************************************************************

# Load mapping dictionary for PA --> Model Grid matching
map_PA2HRRR = np.load('PA_to_HRRRgrid.npy',allow_pickle='TRUE').item()
# *********************************************************************

# file = 102

t0 = timing.time()
print(t0)

for t,time in enumerate(times):
        if t % 100 == 0:
            print("\n\n On %d/%d" % (t, len(times)))
            print("Loop took %f seconds" % (timing.time() - t0))
            t0 = timing.time()

        # Select out the purple air data for that time stamp
        df_pa_hour = COMPARE[COMPARE.time == time]

        # print("Looking at 1 hour of Purple Air data. Number of entries:", len(df_pa_hour))

        # If there are no PA datapoints @ that timestamp, continue to the next time 
        if df_pa_hour.empty:
            continue

        # Open the HRRR data
        try:
            fn ="/global/scratch/users/siennaw/gsi_2024/output/2019_1/wrf_inout_%s" % (to_file_date(time)) 
            hrrr = xr.open_dataset(fn)
            # print("opened file %s" % fn)

            # Smoke before assimilation (INIT = initial)
            smoke_before = hrrr['PM2_5_DRY_INIT'].isel(bottom_top=0).isel(Time=0).values
            smoke_before = np.squeeze(smoke_before).ravel()

            # Smoke data after assimilation 
            smoke_after = hrrr['PM2_5_DRY'].isel(bottom_top=0).isel(Time=0).values
            smoke_after = np.squeeze(smoke_after).ravel()
        except:
            print("Couldn't find file %s" % fn)
            continue
        


        # Loop through all the sensors at that date. 
        for i, row in df_pa_hour.iterrows():

            # Get unique sensor code 
            sensor = row['sensor']

            # Retrieve the PA sensor --> HRRR grid mapping for that location 
            mapping = map_PA2HRRR[sensor]
            if len(mapping) == 0:
                print("No mapping found for sensor %s" % sensor)
                continue
            indicies, distances = zip(*mapping)

            # Convert to numpy arrays
            indicies = np.array(indicies)
            distances = np.array(distances)

            # Inverse distance weighting
            weights = 1 / distances

            # Value before assimilation
            nearest_values = smoke_before[indicies]
            interpolated_value_before = np.sum(weights * nearest_values) / np.sum(weights)

            # Value after assimilation
            nearest_values = smoke_after[indicies]
            interpolated_value_after = np.sum(weights * nearest_values) / np.sum(weights)

            # Save values in the dataframe
            COMPARE.loc[i, "model_before_da"] = interpolated_value_before
            COMPARE.loc[i, "model_after_da"] = interpolated_value_after 
       
        # t0 = timing.time()


COMPARE = COMPARE.dropna(how="any", axis=0)
COMPARE.to_csv("Model2PurpleAir_run=%d.csv" % file, index=False)

print(COMPARE)
        
            




