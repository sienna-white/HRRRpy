import xarray as xr 
import os.path
import pandas  as pd 
import matplotlib.pyplot as plt 
import cartopy.crs as crs
import cartopy
from matplotlib.colors import LogNorm
import numpy as np 
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
import cmocean 
import matplotlib
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import pyplot as plt
import time 

class HRRR:
    '''
    Class definition for Regex objects
    '''
    def __init__(self, fn):
        # assign input text to self.text

        if not os.path.isfile(fn):
            print('File does not exist! Check path name: \t%s' % fn) 
            self.does_not_exist = True
        self.filepath = fn 

        ds = xr.open_dataset(fn)
        self.ds = ds

        self.strip_time_info()

        self.lats = np.squeeze(ds['XLAT'].isel(Time=0)) 
        self.lons = np.squeeze(ds['XLONG'].isel(Time=0))


    def strip_time_info(self):
        date = self.ds.START_DATE
        date = pd.to_datetime(date, format='%Y-%m-%d_%H:%M:00')
        print('Opened model results from %s' % date.strftime('%B %d, %Y @ %H:%M'))
        self.time = date 
        self.time_str = date.strftime('%B %d, %Y at %H:%M')


    def plot_var(self, var, fout=None, level=0, vmin=None, vmax=None): 

        ds = self.ds


        if var in ds.data_vars: 
            pass
        else:
            Exception('This variable is not available.')

        variable  = ds[var].isel(bottom_top=level).isel(Time=0)
        print("plotting:", variable.description)

        # Fixed values for setting up the plot
        cart_proj = crs.LambertConformal() 
        cmap = cmocean.cm.turbid  # Colormap
        lats = self.lats
        lons = self.lons

        # Create plot 
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6,5),subplot_kw={'projection': cart_proj})

        if vmin is None:
            vmin = variable.quantile(0.10).item()
        
        if vmax is None:
            vmax = variable.quantile(0.90).item()

        def mask_array(variable):
            threshold = 0
            return np.ma.array (variable, mask=variable<threshold)

        # Format axes
        ax.coastlines('50m', linewidth=0.8)
        ax.gridlines(alpha = 0.25) 
        ax.add_feature(cartopy.feature.STATES.with_scale('50m'))

        # Axis 1: Variable before assimilation
        mesh = ax.pcolormesh(lons, lats, mask_array(variable), 
                        transform=crs.PlateCarree(), 
                        cmap = cmap, 
                        vmin = vmin, 
                        vmax = vmax)  

        units = variable.units 
        cbar = plt.colorbar(mesh, shrink = 0.4, orientation="horizontal" , label = units)
        cbar.set_label(units)

        text = '%s on %s' % (var, self.time_str) 
        ax.set_title(text)

        plt.tight_layout()

        # Save figure as ...  
        if fout is None:
            fout = os.getcwd()

        fn = os.path.join(fout, (text + '.png'))
        fig.savefig(fn)
        print('Done, saved %s' % fn)