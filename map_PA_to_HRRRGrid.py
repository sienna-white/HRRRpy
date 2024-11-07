import pandas as pd 
from pyproj import Proj, transform, Transformer
import xarray as xr 
import numpy as np 

# From WGS84 to UTM Zone 10 (ESPG:32610)
transform0 = Transformer.from_crs(4326, 32610)


csv = "/global/scratch/users/rasugrue/data/PA_sensors.csv"

df_pa = pd.read_csv(csv)
print("Loaded Purple Air data successfully. Number of sensors:", len(df_pa))

# print(df_pa)
# df_pa = df_pa.iloc[0:20]
lat, lon = df_pa['LATITUDE'], df_pa['LONGITUDE'] 
pax, pay = transform0.transform(lat, lon)
sensors = df_pa['SENSOR_INDEX']

# Load in model grid
model_grid = pd.read_csv("HRRRgrid.csv", header=1)
model_x = model_grid['model_utmx']
model_y = model_grid['model_utmy']

grid_dx = 3000 # meters

dict_out = {} 

for i, (x,y,sensor) in enumerate(zip(pax,pay,sensors)):

    if i%500 == 0:
        print("%d/%d" % (i,len(sensors)))

    # Calculate Euclidean distance between center of grid cell + PA sensor 
    distance2 = (x - model_x)**2 + (y - model_y)**2

    # Indicies of all the grid cells that are within 3km 
    index = (distance2 < grid_dx**2)
    # print("There are %d grid cells near sensor %s " % (sum(index), sensor))

    indices = np.argwhere(index)
    distances = np.sqrt(distance2[index].values)

    dict_out[sensor] = [(i[0], d) for i, d in zip(indices, distances)]

    # Weight is the inverse of the distance (small distance = bigger weight)

data_out = pd.DataFrame.from_dict(dict_out, orient='index') 

np.save('PA_to_HRRRgrid.npy', dict_out) 


data_out_fn = "PA_to_HRRRgrid.csv"
with open(data_out_fn, 'w') as file:
    file.write('purple air sensors matched to index in HRRR-Smoke grid. Each column is a grid index + distance from that point to PA sensor.')
    data_out.to_csv(file, header=True, index=False)


assert(False)
    # Compute the weighted average of the nearest values
    # interpolated_value = np.sum(weights * nearest_values) / np.sum(weights)

