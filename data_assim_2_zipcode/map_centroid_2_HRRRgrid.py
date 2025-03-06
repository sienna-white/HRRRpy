###
# this script will take the output of GSI and give zip-code averages PM values at an hourly basis
# input: 
# wrf_inout_YYYYMMDDHH netcdf files produced from running GSI
# shapefile of zipcodes in CA
# shapefile of census tracts in CA (for poulation weighting)
# output: csv of hourly PM values averaged at the zip code (datetime, zipcode, PM average)
# method:
# for each hourly file
# 1. (OLD THOUGHT) calculate average PM per tract and assign to tract AND centroid within the tract (point) 
# 1. match grid point to nearest population centroid
# 2. calculate population weighted average PM per zipcode AND save file (datetime, zipcode, average)
# once loop is done
# 3. merge all files

###

import geopandas as gpd
import pandas as pd
import xarray as xr
from shapely.geometry import Point
import os
import numpy as np 

# Zip code shapefile
shapefile_path = "/global/home/users/rasugrue/to_zipcodes/ZIP shapefile/California_Zip_Codes.shp"

# Population centroids
centroids_path = "/global/home/users/rasugrue/to_zipcodes/CenPop2020_Mean_TR06.csv"

# Assimilated netcdf file
netcdf_folder = "/global/scratch/users/siennaw/gsi_2024/output/2019_1/"

# Grid centers UTM
grid_centers_utm = "/global/scratch/users/siennaw/scripts/HRRRpy/grid/HRRRgrid.csv"

UTM10 = 32610

# output
output_path = "."
########################################################################################


# [1] Read zipcode shapefile
zip_codes = gpd.read_file(shapefile_path)
zip_codes = zip_codes.to_crs(epsg=UTM10)  # Reproject zip codes to UTM (adjust the EPSG code as needed)
print("Zipcodes read in & reprojected to ESPG:%d" % UTM10)
############################################

# [2] Convert shapefile to centroids
centroids = pd.read_csv(centroids_path)
geometry = [Point(xy) for xy in zip(centroids['LONGITUDE'], centroids['LATITUDE'])]
geo_centroids = gpd.GeoDataFrame(centroids, geometry=geometry)
geo_centroids.set_crs(epsg=4326, inplace=True)    # Set CRS to geographic (WGS84)
geo_centroids = geo_centroids.to_crs(epsg=UTM10)  # Reproject centroids to UTM (adjust EPSG code as needed)
print("Population centroids read in & reprojected to ESPG:%d" % UTM10)
############################################

# [3] Read in grid data from HRRR-Smoke 
grid_centers = pd.read_csv(grid_centers_utm, header=1)
wrf_utm_x = grid_centers['model_utmx'].values.ravel() 
wrf_utm_y = grid_centers['model_utmy'].values.ravel() 
grid_points = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in zip(wrf_utm_x, wrf_utm_y)])


N_grid_pts = len(grid_points)
N_centroids = len(geo_centroids)
closest_cell_to_centroid = np.zeros(N_centroids)

# Loop through each centroid and find the closest grid point in the HRRR-Smoke Grid
for i in range(0, N_centroids):
    if i % 100 == 0:
        print("Processing centroid %d/%d" % (i, N_centroids))
    centroid = geo_centroids.iloc[i].geometry
    distance_from_centroid = grid_points.geometry.distance(centroid)
    closest_cell_to_centroid[i] = distance_from_centroid.idxmin()
print("Done finding closest cells to each centroid!")

# Add the closest grid point index to the dataframe
geo_centroids['closest_HRRR_cell_index'] = closest_cell_to_centroid

# Spatial join to map centroids to zip codes and average PM 
joined = gpd.sjoin(geo_centroids, zip_codes, how='inner') 

# Merge the zip codes to the centroids
geo_centroids = geo_centroids.merge(joined[['ZIP_CODE']], left_index=True, right_index=True)
print("Centroids have been assigned ZIP codes via spatial join.")

geo_centroids.to_file("HRRR_2_CenPop2020.shp")
