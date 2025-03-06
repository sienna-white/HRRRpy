import pandas as pd 
from pyproj import Proj, transform, Transformer


start_date = '2018110800'
ndays = 15 

start_date_dt = pd.to_datetime(start_date, format="%Y%m%d%H")
end_date_dt = start_date_dt + pd.Timedelta(days=ndays)

### Parse month, date, year
assert(end_date_dt.month == start_date_dt.month )
month = start_date_dt.month 
year = start_date_dt.year 

data = []


# Load the entire Purple Air dataset once
pa_data_path = '/global/scratch/users/rasugrue/convert2bufr/validation/validation_data_%d_%d.csv' % (month, year)
df_pa = pd.read_csv(pa_data_path)
print("Loaded Purple Air data successfully. Number of entries:", len(df_pa))


def to_file_date(datetime_obj):
   return time.strftime("%Y%m%d%H")  
tasks = []

times = pd.date_range(start_date_dt, end_date_dt, freq="1h")

for time in times:

        # Select out the purple air data for that time stamp
        datetime_str = time.strftime("%Y-%m-%0d %H:00:00") 
        df_pa_hourly = df_pa[df_pa.time ==time]
        df_pa_hourly.reset_index(inplace=True)

        # If there are no entries @ that timestamp, continue to the next time 
        if df_pa_hourly.empty:
            continue

        try:
            fn ="/global/scratch/users/siennaw/gsi_2024/output/%d/wrf_inout_%s" % (file, to_file_date(time)) 
            hrrr = xr.open_dataset(fn)
        except:
            print("Couldn't find file %s" % date4file)
        continue 


 
        # Loop through 
        for i, row in df_pa_hourly.iterrows():
            print(row)

            sensor_location = (row['latitude'], row['longitude'])


            observed_pm25 = row['PM2_5_ATM_A']  
            print(observed_pm25)
            # if if pd.notna(row['PM2_5_ATM_A'])
            
            # else None
            # if observed_pm25 is None:
            #     continue
            assert(False)

            # Get filepath of the netcdf file that contains both the pre & post DA smoke field 
            fp =  os.path.join(hrrr_data_dir, "wrf_inout_%s" % to_file_date(time))
  

            

            tasks.append((datetime_str, sensor_location, observed_pm25, hrrrI_file, hrrr_file_post))

print(f"Number of tasks: {len(tasks)}")

processing_times = []

def process_task(task):
    datetime_str, sensor_location, observed_pm25, hrrrI_file, hrrr_file_post = task
    start_time = time.time()
    before_pm25, after_pm25 = self.read_and_process_hour(hrrrI_file, hrrr_file_post, sensor_location)
    end_time = time.time()
    processing_time = end_time - start_time
    return datetime_str, sensor_location, observed_pm25, before_pm25, after_pm25, processing_time

results = []
with tqdm(total=len(tasks), desc="Processing files") as pbar:
    for result in Parallel(n_jobs=-1)(delayed(process_task)(task) for task in tasks):
        results.append(result)
        pbar.update(1)

print(f"Number of results: {len(results)}")

for result in results:
    datetime_str, sensor_location, observed_pm25, before_pm25, after_pm25, processing_time = result
    if before_pm25 is not None and after_pm25 is not None:
        data.append([datetime_str, sensor_location[0], sensor_location[1], observed_pm25, before_pm25, after_pm25])
        processing_times.append(processing_time)

df_results = pd.DataFrame(data, columns=['Time', 'Latitude', 'Longitude', 'Observed_PM2.5', 'Before_Assimilation_PM2.5', 'After_Assimilation_PM2.5'])

if save_path:
    df_results.to_csv(save_path, index=False)
    print(f"CSV file saved to {save_path}")
else:
    print(df_results)

# Plotting processing times
if processing_times:
    plt.figure(figsize=(10, 5))
    plt.plot(processing_times, label='Processing Time (s)')
    plt.xlabel('Task Number')
    plt.ylabel('Time (s)')
    plt.title('Processing Time per File')
    plt.legend()
    plt.show()
else:
    print("No processing times recorded")



def read_and_process_hour(self, hrrrI_file, hrrr_file_post, sensor_location):
    before_value = None
    after_value = None
    try:
        ds_pre = xr.open_dataset(hrrrI_file)
        before_value = self.get_value_from_nearest_points(ds_pre, 'PM2_5_DRY', sensor_location[0], sensor_location[1])
    except Exception as e:
        print(f"Error reading {hrrrI_file}: {e}")

    try:
        ds_post = xr.open_dataset(hrrr_file_post)
        after_value = self.get_value_from_nearest_points(ds_post, 'PM2_5_DRY', sensor_location[0], sensor_location[1])
    except Exception as e:
        print(f"Error reading {hrrr_file_post}: {e}")

    return before_value, after_value


def get_value_from_nearest_points2(self, ds, variable_name, sensor_locs):
    lats = ds['XLAT'].isel(Time=0).values
    lons = ds['XLONG'].isel(Time=0).values
    values = ds[variable_name].isel(Time=0, bottom_top=0).values

    # Flatten the lat, lon, and value arrays
    lats_flat = lats.flatten()
    lons_flat = lons.flatten()
    values_flat = values.flatten()

    # Create a KD-tree for fast nearest-neighbor lookup
    tree = cKDTree(np.c_[lats_flat, lons_flat])

    interpolated_values = []
    for loc in sensor_locs:
        lat, lon = loc
        # Find the 4 nearest points
        dist, idx = tree.query([lat, lon], k=4)
        nearest_values = values_flat[idx]

    # Perform inverse distance weighting (IDW)
    if np.any(dist == 0):
        # Handle the case where a sensor is exactly at a grid point
        interpolated_value = nearest_values[dist == 0][0]
    else:
        # Calculate weights as the inverse of the distances
        weights = 1 / dist
        # Compute the weighted average of the nearest values
        interpolated_value = np.sum(weights * nearest_values) / np.sum(weights)

    interpolated_values.append(interpolated_value)

    return interpolated_values
