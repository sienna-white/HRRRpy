###
# this script will take the output of GSI and give zip-code averages PM values at an hourly basis
# input: 
# wrf_inout_YYYYMMDDHH netcdf files produced from running GSI
# shapefile of zipcode population centroids in CA
# output: csv of hourly PM values averaged at the zip code (datetime, zipcode, PM average)
# method:
# first, 
# 1. match centroids to nearest grid point, using kd tree (this works because the grid
#  and centroids are converted to UTM and Euclidean distance can be accurately calculated)
# 2. match each centroid to a zipcode (the field for centroid list FIPS not zipcodes so 
# perform a spatial join of centroid point to zipcode polygons)
# then, for each hourly file
# 3. assign each centroid the PM value from it's nearest grid point (matched in step 1)
# 4. group by zipcode (matched in step 2 above)
# 5. add the datetime
# 6. save as one file
###

import geopandas as gpd
import pandas as pd
import xarray as xr
from shapely.geometry import Point
import os
from scipy.spatial import cKDTree

# paths
shapefile_path = "/global/home/users/rasugrue/to_zipcodes/ZIP shapefile/California_Zip_Codes.shp"
centroids_path = "/global/home/users/rasugrue/to_zipcodes/CenPop2020_Mean_TR06.csv"
netcdf_folder = "/global/scratch/users/siennaw/gsi_2024/output/2019_1/"
output_path = "/global/scratch/users/rasugrue/zipcodes/"
final_output_path = os.path.join(output_path, "zipcode_pm_averages_2019.csv")

# read and reproject ZIP codes
zip_codes = gpd.read_file(shapefile_path)
zip_codes = zip_codes.to_crs(epsg=32610)  # Convert to UTM
print("ZIP codes read in and reprojected.")

# read centroids, convert to GeoDataFrame, and reproject to UTM
centroids = pd.read_csv(centroids_path)
geometry = [Point(xy) for xy in zip(centroids['LONGITUDE'], centroids['LATITUDE'])]
geo_centroids = gpd.GeoDataFrame(centroids, geometry=geometry, crs="EPSG:4326")
geo_centroids = geo_centroids.to_crs(epsg=32610)
print("Centroids loaded, converted to GeoDataFrame, and reprojected to UTM.")

# precompute grid points from the first NetCDF file (assuming grid geometry is constant across files)
first_file = next((f for f in os.listdir(netcdf_folder) if f.startswith("wrf_inout")), None)
if first_file is None:
    raise FileNotFoundError("No NetCDF files found in the folder.")
first_netcdf_path = os.path.join(netcdf_folder, first_file)
with xr.open_dataset(first_netcdf_path) as da:
    lat = da['XLAT'].isel(Time=0).values.flatten()
    lon = da['XLONG'].isel(Time=0).values.flatten()
print("Grid latitudes and longitudes extracted from the first file.")

# create grid points GeoDataFrame (initially in WGS84), then reproject to UTM
grid_points = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in zip(lon, lat)], crs="EPSG:4326")
grid_points = grid_points.to_crs(epsg=32610)
print("Grid points reprojected to UTM.")

# extract (x, y) coordinates for kd-tree construction
grid_coords = [(geom.x, geom.y) for geom in grid_points.geometry]

# Build the kd-tree for the grid points
tree = cKDTree(grid_coords)
print("KD-tree built using grid point coordinates.")

# precompute the nearest grid point index for each centroid using the kd-tree
centroid_coords = [(geom.x, geom.y) for geom in geo_centroids.geometry]
distances, nearest_indices = tree.query(centroid_coords)
geo_centroids['grid_index'] = nearest_indices
print("Nearest grid point indices precomputed for centroids.")

# precompute spatial join: assign each centroid a ZIP code
centroid_zip = gpd.sjoin(geo_centroids, zip_codes, how='inner', predicate='within')
geo_centroids = geo_centroids.merge(centroid_zip[['ZIP_CODE']], left_index=True, right_index=True)
print("Centroids have been assigned ZIP codes via spatial join.")

# process each NetCDF file: update PM values using precomputed kd-tree indices
all_results = []

for filename in os.listdir(netcdf_folder):
    if filename.startswith("wrf_inout"):
        netcdf_path = os.path.join(netcdf_folder, filename)
        print(f"Processing file: {netcdf_path}")
        try:
            with xr.open_dataset(netcdf_path) as da:
                # extract PM field and flatten the array
                flat_pm = da['PM2_5_DRY'].isel(bottom_top=0).isel(Time=0).values.flatten()
            # use the precomputed grid indices to update PM values for each centroid
            geo_centroids['PM'] = flat_pm[geo_centroids['grid_index']]
            # compute average PM by ZIP code
            zip_code_avg = geo_centroids.groupby('ZIP_CODE')['PM'].mean().reset_index()
            # extract datetime from filename (assumes filename ends with _YYYYMMDDHH.nc)
            datetime_str = filename.split("_")[-1].split(".")[0]
            zip_code_avg['datetime'] = pd.to_datetime(datetime_str, format='%Y%m%d%H')
            all_results.append(zip_code_avg)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# concatenate results and save to CSV
final_results = pd.concat(all_results, ignore_index=True)
final_results.to_csv(final_output_path, index=False)
print(f"Saved all ZIP code averages to {final_output_path}")
