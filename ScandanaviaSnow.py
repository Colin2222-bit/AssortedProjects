import os
import cdsapi
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from scipy import stats 
import numpy as np




##**Research question**: Does early season snow depth correlate with mid and late season snow depth in Northern Europe? Additionally, what synoptic patterns are associated with higher and lower snowfall?

##**Hypothesis**: Early season snow will have a moderately strong, but not extremely strong, correlation with mid and late season snowfall. I expect the correlation to be the strongest between early and mid-season. 

#Run once to download data

with open(os.path.expanduser("~/.cdsapirc"), "w") as f:
    f.write("url: https://cds.climate.copernicus.eu/api\n")
    #f.write(key: *your ERA5 key*)

print("File created at:", os.path.expanduser("~/.cdsapirc"))

 

c = cdsapi.Client()


c.retrieve(
    'reanalysis-era5-pressure-levels',
    {
        'product_type': 'reanalysis',
        'variable': "geopotential",
        'pressure_level': ['500', '850'],
        'year': [
        "2015", "2016", "2017",
        "2018", "2019", "2020",
        "2021", "2022", "2023",
        "2024", "2025", 
    ],
        'month': [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12"
    ],
        'day': [
       "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12",
        "13", "14", "15",
        "16", "17", "18",
        "19", "20", "21",
        "22", "23", "24",
        "25", "26", "27",
        "28", "29", "30",
        "31"
    ],
        'time': '00:00',
        'format': 'netcdf',
        "area": [73, 5, 55, 20]
    },
    'download.nc') 

c.retrieve(
  "reanalysis-era5-land",
{
    "product_type": [
        "reanalysis",
        
    ],
    "variable": ["snow_depth_water_equivalent"],
    "year": [
        "2015", "2016", "2017",
        "2018", "2019", "2020",
        "2021", "2022", "2023",
        "2024", "2025"
    ],
    "month": [
        "01", "02", "03",
        "04", "09",
        "10", "11", "12"
    ],
    "day": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12",
        "13", "14", "15",
        "16", "17", "18",
        "19", "20", "21",
        "22", "23", "24",
        "25", "26", "27",
        "28", "29", "30",
        "31"
    ],
    "time": ["00:00"],
    "format": 'netcdf',
    "download_format": "unarchived",
    "area": [73, 5, 55, 20]
},
    'snowdata.nc')



ds = xr.open_dataset('download.nc', chunks={'time': 100})
dssnow = xr.open_dataset('snowdata.nc', chunks={'time': 100})

ds



dsgeo = ds.sel(valid_time = ds.valid_time.dt.month.isin([1,2,3,4,9,10,11,12]))
dsgeo['geop']= dsgeo.z/9.80655




dsgeo

dsgeo = dsgeo.rename({'valid_time': 'time'})
dsgeo = dsgeo.rename({'pressure_level': 'pressure'})
dsgeo = dsgeo.rename({'latitude': 'lat'})
dsgeo = dsgeo.rename({'longitude': 'lon'})



dssnow = dssnow.rename({'valid_time': 'time'})
dssnow = dssnow.rename({'latitude': 'lat'})
dssnow = dssnow.rename({'longitude': 'lon'})
dssnow = dssnow.rename({'sd': 'snowdepth'})

geomean = dsgeo.geop.mean(dim='time')

dsgeo = dsgeo.drop_vars('z')

dsgeo

dssnowgrid=dssnow.where(dssnow.snowdepth<0.75)
january = dssnowgrid.snowdepth.groupby(dssnowgrid.time.dt.month).mean().isel(month=0)
april = dssnowgrid.snowdepth.groupby(dssnowgrid.time.dt.month).mean().isel(month=3)



 I had to filter out snow water equivalent below 0.5m because the data was heavily skewed by a few select points (I assume mountains). While that seems aggressive, remember that this is snow water equivalent, so that would represent about 5m of snow (more if powdery, less if wet). The majority of the area has less than this amount of snow at any given time - there are snippets (such as the January 1, 2025) graph where a more significant portion of the map, but on the all-time and monthly January averages spatial plots, these high values get smoothed out enough. The highest SWE occurs near the coast of Norway (but not right on the coast) with depth dropping as you move further into Southeastern Sweden. An obvious seasonal cycle occurred in the temporal plots, with an anomalously high snow depth in 2018 for whatever reason. The geopotential height plots were less surprising; with a simple north-south outlook apparent on yearly and monthly timescales. There was an extremely low 850 geopotential height in 2020, which was interesting. I then did a simple re-grid of the data using interp_like similar to in class. Because I am worried about synoptic scale flow, I regridded the finer 9km snowfall resolution on the coarser 31km resolution using the nearest method. Due to the smooth nature of snowfall, this decision is justifiable.

corr = xr.corr(january,april)





corr.compute()

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 10))



jan = dssnowgrid.snowdepth.sel(time=dssnowgrid.time.dt.month == 1).resample(time = '1YS').mean()
oct = dssnowgrid.snowdepth.sel(time=dssnowgrid.time.dt.month == 10).resample(time = '1YS').mean()


corr6=xr.corr(jan, oct.shift(time=1), dim='time').compute()
corr6.plot(ax=axes[0,0])
axes[0,0].set_title('October')
axes[0,0].set_xlabel('')
axes[0,0].set_ylabel('Latitude')

nov = dssnowgrid.snowdepth.sel(time=dssnowgrid.time.dt.month == 11).resample(time = '1YS').mean()

corr7=xr.corr(nov.shift(time=1), jan, dim='time').compute()
corr7.plot(ax=axes[0,1])
axes[0,1].set_title('November')
axes[0,1].set_xlabel('')
axes[0,1].set_ylabel('')

dec = dssnowgrid.snowdepth.sel(time=dssnowgrid.time.dt.month == 12).resample(time = '1YS').mean()

corr2=xr.corr(dec.shift(time=1), jan, dim='time').compute()
corr2.plot(ax=axes[0,2])
axes[0,2].set_title('December')
axes[0,2].set_xlabel('')
axes[0,2].set_ylabel('')


feb = dssnowgrid.snowdepth.sel(time=dssnowgrid.time.dt.month == 2).resample(time = '1YS').mean()

corr3=xr.corr(jan, feb, dim='time').compute()
corr3.plot(ax=axes[1,0])
axes[1,0].set_title('February')
axes[1,0].set_xlabel('Longitude')
axes[1,0].set_ylabel('Latitude')

mar = dssnowgrid.snowdepth.sel(time=dssnowgrid.time.dt.month == 3).resample(time = '1YS').mean()

corr4=xr.corr(jan, mar, dim='time').compute()
corr4.plot(ax=axes[1,1])
axes[1,1].set_title('March')
axes[1,1].set_xlabel('Longitude')
axes[1,1].set_ylabel('')


aprl = dssnowgrid.snowdepth.sel(time=dssnowgrid.time.dt.month == 4).resample(time = '1YS').mean()

corr5=xr.corr(jan, aprl, dim='time').compute()
corr5.plot(ax=axes[1,2])
axes[1,2].set_title('April')
axes[1,2].set_xlabel('Longitude')
axes[1,2].set_ylabel('')

fig.suptitle("Correlation between January Snowfall and Other Months in Northern Europe")

Now completes phase one of my project, which focused on snow data. I found the correlation at every pixel in the dataset using the variance between January and several other months. The results somewhat support my hypothesis that early season snowfall would correlate to late season snowfall, which is more obvious using snow DEPTH versus snowfall per month. This is likely why southern areas have less correlation, as the snow melts and inter-season randomness takes over. However, in Northern Europe, the snow stays on the ground due to the cold climate, which of course would make the correlation increase. I am still surprised by how strong the correlation is in the North, however. I will likely go back and compare October to March or April, as it would be a more true test as there is a better chance of some snow melting in between. I start my regridding, anomaly calculations, and eventual further correlations between the two datasets below.

For most of the country, October 1 snow depth correlated with April snow depth, particularly in Eastern Norway and Northwestern Sweden. However, in Southern Sweden and Coastal Norway, there was actually a negative correlation. The melting idea
is still my main explanation for the Southern area, but I am not sure of the strong negative correlation in coastal areas. 


corrOctMar = xr.corr(aprl, oct.shift(time=1), dim='time')
corrOctMar.plot()
plt.title("Correlation between October Snow Depth and April Snow Depth in Northern Europe")
plt.xlabel('Longitude')
plt.xlabel('Latitude')


snowregrid= dssnowgrid.interp_like(dsgeo.geop, method = 'nearest')



snowregrid.snowdepth.mean(dim='time').plot()
snowregrid

Before the second part of the project, I had to re-grid the data and coarsen the snow depth Dataset based on the nearest pixel. This is to make sure EOFs are well behaved. The datasets already had the same amount of time steps, which is also helpful. 

I made the filter less aggressive to avoid excessive null values, which might affect EOF anomalies. I found the climatology for both geopotentials and SWE similar to what we did in class. Note the extremely low geopotential anomaly near 2020. 

from eofs.standard import Eof

values = geoanomaly.values
wgts = np.cos(np.deg2rad(geoanomaly.lat)).values[:, np.newaxis]
solver =  Eof(values, weights=wgts)
eof1 = solver.eofs(neofs=10)
pc1  = solver.pcs(npcs=10, pcscaling=0)
varfrac = solver.varianceFraction()
lambdas = solver.eigenvalues() 

fig1, axes1 = plt.subplots(3, 1, figsize=(9, 12), 
                           subplot_kw={'projection': ccrs.PlateCarree()})

for i in range(0,3):
    ax = axes1[i]
    cs = ax.contourf(geoanomaly.lon, geoanomaly.lat, eof1[i,:,:].squeeze(), 
                     cmap='RdBu_r', transform=ccrs.PlateCarree())
    cb = plt.colorbar(cs, ax=ax, orientation='vertical', pad=0.02)
    cb.set_label('EOF', fontsize=12)
    ax.set_title(f'EOF Mode {i+1}', fontsize=14)
    ax.coastlines()

plt.tight_layout()
plt.show()


fig2, axes2 = plt.subplots(3, 1, figsize=(9, 12))

months = np.linspace(2015, 2025, geoanomaly2.time.size)

for i in range(3):
    ax = axes2[i]

    ax.plot(months, pc1[:, i], linewidth=2)
    ax.axhline(0, color = 'k')
    
    ax.set_title('Time Series PC Amplitude')
    ax.set_ylabel('PC Amplitude')    
    ax.set_ylim(np.min(pc1.squeeze()), np.max(pc1.squeeze()))
    ax.set_xlabel('Year')

plt.tight_layout()
plt.show()

pc1da = xr.DataArray(
    pc1[:, 0], 
    coords={'time': geoanomaly.time}, 
    dims=['time'],
    name='pc1da'
)


corr2 = xr.corr(pc1da,anomaly)

corr2.compute()

pc1da2 = xr.DataArray(
    pc1[:, 1], 
    coords={'time': geoanomaly.time}, 
    dims=['time'],
    name='pc1da2'
)

corr3 = xr.corr(pc1da2,anomaly)

corr3.compute()

pc3da1 = xr.DataArray(
    pc1[:, 2], 
    coords={'time': geoanomaly.time}, 
    dims=['time'],
    name='pc1da3'
)

corr4 = xr.corr(pc3da1,anomaly)

corr4.compute()

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(6,15), constrained_layout=True)


correlationmap = xr.corr(pc1da, anomaly, dim='time')
correlationmap.plot(ax=axes[0])
axes[0].set_title('500 PC1 vs Snow Depth')
axes[0].set_xlabel('Lon')
axes[0].set_ylabel('Lat')

correlationmap2 = xr.corr(pc1da2, anomaly, dim='time')
correlationmap2.plot(ax=axes[1])
axes[1].set_title('500 PC2 vs Snow Depth')
axes[1].set_xlabel('Lon')
axes[1].set_ylabel('Lat')

correlationmap3 = xr.corr(pc3da1, anomaly, dim='time')
correlationmap3.plot(ax=axes[2])
axes[2].set_title('500 PC3 vs Snow Depth')
axes[2].set_xlabel('Lon')
axes[2].set_ylabel('Lat')

plt.show()
EOF data for the other pressure level was extremely similar, which makes sense intuitively, but was even more similar than expected. I had to double check to make sure the pressure levels were actually different.

values2 = geoanomaly2.values
wgts2 = np.cos(np.deg2rad(geoanomaly2.lat)).values[:, np.newaxis]
solver =  Eof(values2, weights=wgts2)
eof2 = solver.eofs(neofs=10)
pc2  = solver.pcs(npcs=10, pcscaling=0)
varfrac2 = solver.varianceFraction()
lambdas2 = solver.eigenvalues() 

fig1, axes1 = plt.subplots(3, 1, figsize=(9, 12), 
                           subplot_kw={'projection': ccrs.PlateCarree()})

for i in range(0,3):
    ax = axes1[i]
    cs = ax.contourf(geoanomaly2.lon, geoanomaly2.lat, eof2[i,:,:].squeeze(), 
                     cmap='RdBu_r', transform=ccrs.PlateCarree())
    cb = plt.colorbar(cs, ax=ax, orientation='vertical', pad=0.02)
    cb.set_label('EOF', fontsize=12)
    ax.set_title(f'EOF Mode {i+1}', fontsize=14)
    ax.coastlines()

plt.tight_layout()
plt.show()


fig2, axes2 = plt.subplots(3, 1, figsize=(9, 12))

months = np.linspace(2015, 2025, geoanomaly2.time.size)

for i in range(3):
    ax = axes2[i]

    ax.plot(months, pc2[:, i], linewidth=2)
    ax.axhline(0, color = 'k')
    
    ax.set_title('Time Series PC Amplitude')
    ax.set_ylabel('PC Amplitude')    
    ax.set_ylim(np.min(pc2.squeeze()), np.max(pc2.squeeze()))
    ax.set_xlabel('Year')

plt.tight_layout()
plt.show()

pc2da1 = xr.DataArray(
    pc2[:, 0], 
    coords={'time': geoanomaly.time}, 
    dims=['time'],
    name='pc2da1'
)


corr500 = xr.corr(pc2da1,anomaly)

corr500.compute()

pc2da2 = xr.DataArray(
    pc2[:, 1], 
    coords={'time': geoanomaly.time}, 
    dims=['time'],
    name='pc2da2'
)


c2orr500 = xr.corr(pc2da2,anomaly)

c2orr500.compute()

pc3da2 = xr.DataArray(
    pc2[:, 2], 
    coords={'time': geoanomaly.time}, 
    dims=['time'],
    name='pc3da2'
)

c3orr500 = xr.corr(pc3da2,anomaly)

c3orr500.compute()

The resulting correlation maps were also similar for PC1 and PC3. However, PC2 changed completely, and now had a similar pattern to PC1 (as opposed to the reverse for the first level). There was generally less snow with the PC1 synoptic pattern even in the South this time (save for a stripe in Northern Norway). PC2 had a more pronounced less snow South, more snow North divide, and PC3 had a positive correlation in the central areas of the bounding box sandwiched between two negative correlations. 

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(6,15))


correlationmap4 = xr.corr(pc2da1, anomaly, dim='time')
correlationmap4.plot(ax=axes[0])
axes[0].set_title('500 PC1 vs Snow Depth')
axes[0].set_xlabel('Lon')
axes[0].set_ylabel('Lat')

correlationmap5 = xr.corr(pc2da2, anomaly, dim='time')
correlationmap5.plot(ax=axes[1])
axes[1].set_title('500 PC2 vs Snow Depth')
axes[1].set_xlabel('Lon')
axes[1].set_ylabel('Lat')

correlationmap6 = xr.corr(pc3da2, anomaly, dim='time')
correlationmap6.plot(ax=axes[2])
axes[2].set_title('500 PC3 vs Snow Depth')
axes[2].set_xlabel('Lon')
axes[2].set_ylabel('Lat')

plt.tight_layout()
plt.show()
