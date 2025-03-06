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
# zip_codes = gpd.read_file(shapefile_path)
# zip_codes = zip_codes.to_crs(epsg=UTM10)  # Reproject zip codes to UTM (adjust the EPSG code as needed)
# print("Zipcodes read in & reprojected to ESPG:%d" % UTM10)
############################################

# [2] Convert shapefile to centroids
# centroids = pd.read_csv(centroids_path)
# geometry = [Point(xy) for xy in zip(centroids['LONGITUDE'], centroids['LATITUDE'])]
# geo_centroids = gpd.GeoDataFrame(centroids, geometry=geometry)
# geo_centroids.set_crs(epsg=4326, inplace=True)    # Set CRS to geographic (WGS84)
# geo_centroids = geo_centroids.to_crs(epsg=UTM10)  # Reproject centroids to UTM (adjust EPSG code as needed)
# print("Population centroids read in & reprojected to ESPG:%d" % UTM10)
############################################

# [3] Read in grid data from HRRR-Smoke 
grid_centers = pd.read_csv(grid_centers_utm, header=1)
wrf_utm_x = grid_centers['model_utmx'].values.ravel() 
wrf_utm_y = grid_centers['model_utmy'].values.ravel() 
grid_points = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in zip(wrf_utm_x, wrf_utm_y)])

# wrf_lon = grid_centers['model_lon'].values
# wrf_lat = grid_centers['model_lon'].values
import numpy as np 
from affine import Affine

wrf_lon = np.squeeze(grid_centers['XLAT'].values)
wrf_lat = np.squeeze(grid_centers['XLONG'].values)

print(wrf_lon.shape)
ny, nx = wrf_lon.shape
grid_points = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in zip(wrf_lon.ravel(), wrf_lat.ravel())])

# Compute approximate pixel resolution (assume uniform spacing)
lat_res = (wrf_lat[0, 1] - wrf_lat[0, 0])  # Approximate latitude resolution
lon_res = (wrf_lon[1, 0] - wrf_lon[0, 0])  # Approximate longitude resolution

# Define the affine transform (top-left corner and resolution)
transform = Affine(lon_res, 0, wrf_lon[0, 0],  # X resolution and top-left X
                   0, lat_res, wrf_lat[0, 0])  # Y resolution and top-left Y

# Rasterize the shapefile onto the WRF grid
mask = rasterize(
    [(geom, 1) for geom in grid_points.geometry],  # List of (geometry, value)
    out_shape=(ny, nx),  # Output raster shape (same as WRF grid)
    transform=transform,  # Affine transform to align pixels
    fill=0,  # Default value for pixels outside the shapefile
    all_touched=True,  # Consider all pixels touched by the shape
    dtype=np.uint8
)

print(mask)


assert(False)
# for all hours
all_results = pd.DataFrame()

# loop through all NetCDF files in the wrfinout output folder
for filename in os.listdir(netcdf_folder):
    if filename.startswith("wrf_inout"):
        netcdf_path = os.path.join(netcdf_folder, filename)
        print(f"Processing file: {netcdf_path}")

        try:
            da = xr.open_dataset(netcdf_path)

            # get latitude, longitude, and after assimilation concentration data
            after_pm = da['PM2_5_DRY'].isel(bottom_top=0).isel(Time=0).values 

            # flatten data for processing
            lat_flat = lat.flatten()
            lon_flat = lon.flatten()
            after_pm_flat = after_pm.flatten()
            
            # create a GeoDataFrame 
            grid_points = gpd.GeoDataFrame({
                'PM': after_pm_flat
            }, geometry=[Point(lon, lat) for lon, lat in zip(lon_flat, lat_flat)])
            grid_points.set_crs(epsg=4326, inplace=True)  
            grid_points = grid_points.to_crs(epsg=32610)  # reproject grid points to UTM
            print("grid points reprojected to UTM")

            # calculate the distance between grid and centroids
            distances = geo_centroids.geometry.apply(lambda point1: grid_points.geometry.distance(point1))

            # find the index of the closest point 
            closest_indices = distances.idxmin(axis=1)
            geo_centroids['closest_point_index'] = closest_indices
            geo_centroids['closest_point'] = grid_points.loc[closest_indices].reset_index(drop=True)

            print(geo_centroids.head(5))

            # spatial join to map centroids to zip codes and average PM 
            joined = gpd.sjoin(geo_centroids, zip_codes, how='inner', op='within')
            zip_code_avg = joined.groupby('ZIP_CODE')['PM'].mean().reset_index()  

            # add datetime information from the file name
            datetime_str = filename.split("_")[-1].split(".")[0]  # YYYYMMDDHH
            zip_code_avg['datetime'] = pd.to_datetime(datetime_str, format='%Y%m%d%H')

            # append results 
            all_results = pd.concat([all_results, zip_code_avg], ignore_index=True)

            # close netcdf
            da.close()

        except Exception as e:
            print(f"Error processing {filename}: {e}")

# save the total results to a CSV file
final_output_path = os.path.join(output_path, "zipcode_pm_averages_2019.csv")
all_results.to_csv(final_output_path, index=False)
print(f"Saved all zip code averages to {final_output_path}")

