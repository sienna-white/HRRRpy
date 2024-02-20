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
import pandas as pd 

class HRRR:
    '''
    Class definition for Regex objects
    '''
    def __init__(self, fn):
        # assign input text to self.text
        self.filepath = fn 

        if not os.path.isfile(fn):
            self.does_not_exist = True
            Exception('File does not exist! Check path name: \t%s' % fn) 
            return 

        else: 
            ds = xr.open_dataset(fn)
            self.ds = ds
            self.strip_time_info()
            self.lats = np.squeeze(ds['XLAT'].isel(Time=0)) 
            self.lons = np.squeeze(ds['XLONG'].isel(Time=0))
            self.check_if_analysis()

    def check_if_analysis(self):
        ''' Check if this netcdf is output from GSI''' 
        variables = self.ds.data_vars 
        #print(variables)
        if 'PM2_5_DRY_INIT' in variables:
            print('This is a HRRR Analysis Field!')
            self.analysis = True 
        else:
            self.analysis = False 


    def strip_time_info(self):
        ''' Read out the datetime string the model date. Save in various formats''' 
        date = self.ds.START_DATE
        date = pd.to_datetime(date, format='%Y-%m-%d_%H:%M:00')
        print('Opened model results from %s' % date.strftime('%B %d, %Y @ %H:%M'))
        self.time = date 
        self.time_str = date.strftime('%B %d, %Y at %H:%M')

    def get_ds(self):
        return self.ds

    def get_extent(self):
        extent = (self.lons.min(), self.lons.max(), self.lats.min(), self.lats.max())
        return extent

############################################
#####       PLOT VARIABLE             ######
############################################
    def plot_var(self, var, fout=None, level=0, vmin=None, vmax=None, color='turbid'): 

        ds = self.ds


        if var in ds.data_vars: 
            pass
        else:
            Exception('This variable is not available.')

        variable  = ds[var].isel(bottom_top=level).isel(Time=0)
        print("plotting:", variable.description)

        # Fixed values for setting up the plot
        cart_proj = crs.PlateCarree() #crs.LambertConformal() 

        # Colormap
        cmap = cmocean.cm.matter
       
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
        #ax.coastlines('50m', linewidth=0.8)
        ax.gridlines(alpha = 0.25) 
        ax.add_feature(cartopy.feature.STATES.with_scale('50m'))

        # Axis 1: Variable before assimilation
        mesh = ax.pcolormesh(self.lons, self.lats, mask_array(variable), 
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
        fig.savefig(fn, dpi=300) 
        print('Done, saved %s' % fn)

############################################
#####       PLOT COMPARISON           ######
############################################
    def plot_comparison(self, vmax=500): 
        if self.analysis:
            pass
        else: 
            print('Cannot plot pre/post PM2.5 field, this is not GSI output!')
            return 

        # Fixed values for setting up the plot
        cart_proj = crs.PlateCarree() #crs.LambertConformal() 
        cmap = cmocean.cm.tempo     # Colormap
        units = r'$\mu$g/m$^3$'

        # Create plot 
        fig, axs = plt.subplots(nrows=1,ncols=3, figsize=(11,5),subplot_kw={'projection': cart_proj})

        ds = self.ds 
        var_before       = ds['PM2_5_DRY_INIT'].isel(bottom_top=0).isel(Time=0)
        var_after        = ds['PM2_5_DRY'].isel(bottom_top=0).isel(Time=0)
        difference = var_after - var_before

        def mask_array(variable):
            threshold = -2 
            return np.ma.array (variable, mask=variable<threshold)

        def add_cbar(ax, mappable):
            cbar = plt.colorbar(mappable, ax=ax, shrink = 0.6,  orientation="horizontal" )
            cbar.set_label(units)

        # Format axes
        for ax in axs:     
            ax.coastlines('50m', linewidth=0.8)
            ax.gridlines(alpha = 0.25) 
            ax.add_feature(cartopy.feature.STATES.with_scale('50m'))
            # ax.set_extent([-88, -72, 44, 48], crs=crs.PlateCarree())

        # Axis 1: Variable before assimilation
        a = axs[0].pcolormesh(self.lons, self.lats, mask_array(var_before), transform=crs.PlateCarree(), 
                        cmap=cmocean.cm.turbid, vmin = 0, vmax = vmax) 
        add_cbar(axs[0], a)
        axs[0].set_title('Background field')

        # Axis 2: Variable after assimilation
        a = axs[1].pcolormesh(self.lons, self.lats, mask_array(var_after), transform=crs.PlateCarree(), 
                        cmap=cmocean.cm.turbid, vmin = 0, vmax = vmax) 
        add_cbar(axs[1], a)
        axs[1].set_title('Resulting Analysis Field')

        # Axis 3: Difference between the two
        lim = np.max(abs(difference.values))
        a = axs[2].pcolormesh(self.lons, self.lats, difference, transform=crs.PlateCarree(), 
                        cmap=cmocean.cm.balance, vmin = -lim, vmax = lim)  
        axs[2].set_title('Difference (Analysis- Bkg)')
        add_cbar(axs[2], a)

        text = 'Pre and post-assimilation PM2.5 on %s' % self.time_str
        plt.suptitle(text)
        plt.tight_layout()

        # Name to save figure as 
        fn = 'Comparing pre v post assimilation PM25 at %s.png' % self.time_str
        fig.savefig(fn, dpi=300) 
        print('Done, saved %s' % fn)

############################################
#####       PLOT WITH DATA            ######
############################################
    def plot_variable_with_data(self, data_fn=None, before=False, vmax=500): 

        if data_fn==None:
            print('No data filename provided!')
        else: 
             pass 

        if before: 
            print('Plotting INTIAL PM2.5 VALUES')
            if self.analysis:
                var = 'PM2_5_DRY_INIT'
            else:
                var= 'PM2_5_DRY'
            assimilation_status = 'before DA'
            
        else:
            print('Plotting post-analysis PM2.5 values.')
            var = 'PM2_5_DRY'
            assimilation_status = 'after DA'

        title = 'HRRR-Smoke concentration plotted w/ AQS obs data at %s (%s)(' % (self.time_str, assimilation_status)

        # Fixed values for setting up the plot
        cart_proj = crs.PlateCarree() #crs.LambertConformal() 
        cmap = cmocean.cm.matter     # Colormap
        units = r'$\mu$g/m$^3$'

        # Create plot 
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8,5),subplot_kw={'projection': cart_proj})
        ax.set_extent(self.get_extent())

        ds = self.ds 
        variable       = ds[var].isel(bottom_top=0).isel(Time=0)

        def mask_array(variable):
            threshold = 0 
            return np.ma.array (variable, mask=variable<threshold)

        def add_cbar(ax, mappable):
            cbar = plt.colorbar(mappable, shrink = 0.4)
            cbar.set_label(units, rotation=270, labelpad=20)

        # Format axes
        ax.coastlines('50m', linewidth=0.8)
        ax.gridlines(alpha = 0.25) 
        ax.add_feature(cartopy.feature.STATES.with_scale('50m'))

        # Read in observational data
        data = pd.read_csv(data_fn) 

        # Axis 1: Variable before assimilation
        a = ax.pcolormesh(self.lons, self.lats, mask_array(variable), transform=crs.PlateCarree(), 
                        cmap=cmap, vmin = 0, vmax = vmax) 
        add_cbar(ax, a)
        ax.scatter(x = data.longitude, y = data.latitude,  c = data['PM2.5'], 
                     vmin = 0, vmax = vmax, cmap=cmap, edgecolors='black', label = 'AQS observed PM2.5')

        ax.set_title(title)
        ax.legend()
        plt.tight_layout()

        # Name to save figure as 
        fn = 'HRRR-Smoke concentration plotted with AQS obs data at %s (%s).png' % (self.time_str, assimilation_status)
        fig.savefig(fn, dpi=300) 
        print('Done, saved %s' % fn)
