import pandas as pd 
import os 
# Create an hourly timeseries for a year

year = 2019
times_daily = pd.date_range(start='%d-01-01' % year, end='%d-12-31' % year, freq='D')

# Convert to just the date
times_daily = pd.to_datetime(times_daily)
times_daily = [time_daily.date() for time_daily in times_daily]

# Initilize the output dataframe
output = pd.DataFrame(index=times_daily)

for hour in range(0, 24):
    output['%02d' % hour] = 0 

# directory = "/global/scratch/users/siennaw/gsi_2024/grib2nc/finished/"
directory = "/global/scratch/users/rasugrue/convert2bufr/bufr_AQS/"

full_days = 0

missing = [] 
for day in times_daily:

    count = 0 

    for hour in range(0, 24):
        datestring = "%s%02d" % (day.strftime('%Y%m%d'), hour)

    # # Check if the file exists
        file_name = directory + 'HourlyPM_%s.bufr' % datestring

        if os.path.exists(file_name):
            # print("\tFile exists: %s" % file_name)
            count += 1 
            output.loc[day, '%02d' % hour] = 1
        else:
            missing.append(datestring) #  output.loc[day, 'exists'] = False
    
    print("Checked for files on day %s [%d/24]" % (day, count))
    if count == 24:
        full_days += 1

output.to_csv('inventory_%d_AQS.csv' % year)

print("Number of full days: %d" % full_days)
print("Number of missing days: %d" % (len(missing)))

# if not os.path.exists(metgrid_file_name):
#   print('Metgrid file does not exist.')
#   sys.exit(1)
