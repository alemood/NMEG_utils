"""
    export_daily_soilmet.py
    -----------------------

    Script to create and export daily NMEG soilmet files for use in R 
    (or elsewhere). Similar to export_daily_aflx.py.
    
"""
import sys
# laptop
sys.path.append( 'C:/Code/NMEG_utils/py_modules/' )
import load_nmeg as ld
import transform_nmeg as tr
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import pandas as pd

sm_path = 'C:/Research_Flux_Towers/Ameriflux_files/processed_soil/'

# Years to load
startyr = 2007
endyr = 2016
# Sites to load
#sites = ['Seg', 'Ses', 'Sen', 'Wjs', 'Mpj', 'Mpg', 'Vcp', 'Vcm' , 'Vcs']
#altsites = ['GLand', 'SLand', 'New_GLand', 'JSav', 'PJ', 'PJ_girdle',
#	    'PPine', 'MCon','MCon_SS']
#sites = ['Seg', 'Ses', 'Sen', 'Wjs', 'Vcp', 'Vcm', 'Vcs']
#altsites = ['GLand', 'SLand', 'New_GLand', 'JSav', 'PPine', 'MCon', 'MCon_SS']
sites = ['Mpj']
altsites = ['PJ']

# Fill a dict with multiyear dataframes for each site in sites
hourly = { x : 
        ld.get_multiyr_soilmet( x, sm_path, ext='qc_rbd',
            startyear=startyr, endyear=endyr) 
        for x in altsites }

# Add 3 soil moisture columns of different depth ranges
# Also interpolate over missing values
depth_rng = [list(range(0, 6)), list(range(6, 23)), list(range(23, 66))]
depth_str = ['shall', 'mid', 'deep']

def get_depth_mean( df, var,  d_string, d_range ):
    # Extract columns matching depth range
    cols = [h for h in df.columns if var in h and 'tcor' not in h]
    d_range = [str(i) for i in d_range] # Convert to string list
    col_select = list()
    for depth in d_range:
        get_col = [k for k in cols if '_' + depth + 'p' in k 
                or '_' + depth + '_' in k]
        col_select = col_select + get_col
    
    # Calculate depth range SWC mean
    df[d_string + '_swc'] = df[col_select].mean(axis=1, skipna=True)
    
    return(df)
  
    
## Make night time and day time hourly files
#         hourly['mynewkey'] = 'mynewvalue'
## Calculate integrated c fluxes
#c_flux_sums = sum_30min_c_flux( df[ c_fluxes ] )
## Calculate day and night integrated c fluxes. KLUDGE. FIXME
#c_night_flux = c_flux_sums.FC_F_g_int[ df.NIGHT_F == 1 ]
#c_day_flux   = c_flux_sums.FC_F_g_int[ df.NIGHT_F == 0 ]
         
# Resample to daily means
#daily = { x : hourly[x].resample('1D').mean()
#        for x in hourly.keys() }:
            
daily = {}         
for s in hourly.keys():
    df = hourly[s]
    df_shall = get_depth_mean(df, 'SWC', depth_str[0], depth_rng[0])
    df['shall_swc_night'] = np.nan
    df['shall_swc_day'] = np.nan
    df.loc[df.NIGHT==1, 'shall_swc_night'] = df_shall.shall_swc[df.NIGHT==1]
    df.loc[df.NIGHT==0, 'shall_swc_day'] = df_shall.shall_swc[df.NIGHT==0]
    df.drop('shall_swc', 1, inplace=True)
    df = df.resample('1D').mean()
    daily[s] = df
    
# Replace alternate sitenames with ameriflux style names
for i, asite in enumerate(altsites):
    daily[sites[i]] = daily.pop(asite)


def get_depth_mean( df, var,  d_string, d_range ):
    # Extract columns matching depth range
    cols = [h for h in df.columns if var in h and 'tcor' not in h]
    d_range = [str(i) for i in d_range] # Convert to string list
    col_select = list()
    for depth in d_range:
        get_col = [k for k in cols if '_' + depth + 'p' in k 
                or '_' + depth + '_' in k]
        col_select = col_select + get_col
    
    # Calculate depth range SWC mean
    df[d_string + '_swc'] = df[col_select].mean(axis=1, skipna=True)
    
    return(df)

def get_depth_mean_interp( df, site ):
    df['shall_swc_interp'] = df.shall_swc.interpolate(method='pchip')
    df['mid_swc_interp'] = df.mid_swc.interpolate(method='pchip')
    df['deep_swc_interp'] = df.deep_swc.interpolate(method='pchip')
    df.shall_swc.plot(title=site, legend=True)
    df.mid_swc.plot(title=site, legend=True)
    df.deep_swc.plot(title=site, legend=True)
    df.shall_swc_interp.plot(title=site, legend=True)
    df.mid_swc_interp.plot(title=site, legend=True)
    df.deep_swc_interp.plot(title=site, legend=True)
    plt.show()

    return(df)

# Append means for each depth range
for i in range(0, 3):
    daily = { x : get_depth_mean(daily[x], 'SWC', depth_str[i], depth_rng[i])
        for x in daily.keys() }

# Remove some bad data

# Early data from Seg (2007-spring 2009) looks different from later years
# There is a bit of a level shift - consider removing it
#idx = daily['Seg'].index.year < 2010
#daily['Seg'].shall_swc[idx] = np.nan
#daily['Seg'].mid_swc[idx] = np.nan
#daily['Seg'].deep_swc[idx] = np.nan

# There is a level shift in the soil water content data for SLand in May 2011
# The code below removes the day of the shift and then shifts data from before
# this so things match better (only affects depth averages)

# UNCOMMENT LINES BELOW WHEN PROCESSING ALL SITES!

#daily['Ses'].mid_swc[daily['Ses'].index==dt.datetime(2011, 5, 23)] = np.nan
#daily['Ses'].deep_swc[daily['Ses'].index==dt.datetime(2011, 5, 23)] = np.nan
#
#idx = daily['Ses'].index < dt.datetime(2011, 5, 23)
#daily['Ses'].shall_swc[idx] = daily['Ses'].shall_swc[idx] + 0.022
#daily['Ses'].mid_swc[idx] = daily['Ses'].mid_swc[idx] - 0.025
#daily['Ses'].deep_swc[idx] = daily['Ses'].deep_swc[idx] - 0.037

# Append interpolated means for each depth range
daily = { x : get_depth_mean_interp(daily[x], x) for x in daily.keys() }
#daily = { x :  }

import subprocess as sp
git_sha = sp.check_output(
        ['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

for site in sites:
    meta_data = pd.Series([('site: {0}'.format(site)),
        ('date generated: {0}'.format(str(dt.datetime.now()))),
        ('script: export_daily_soilmet.py'),
        ('git HEAD SHA: {0}'.format(git_sha)),('--------')])
    with open('../processed_data/daily_soilmet/US-' + site +
            '_daily_soilmet.csv', 'w') as fout:
        fout.write('---file metadata---\n')
        meta_data.to_csv(fout, index=False)
        daily[site].to_csv(fout, na_rep='NA')

# For exporting monthly shallow, mid, and deep files
#outpath = '/home/greg/current/NMEG_utils/processed_data/'


# Pull out shall
#rbd_i = tr.get_var_allsites(daily, 'shall_swc_interp', sites, startyear=startyr, endyear=endyr)
#rbd_i = rbd_i.resample( '1M', how='mean' )
# Write files to outpath
#rbd_i.to_csv(outpath + 'NMEG_monthly_shallSWC.csv')

# Pull out mid
#rbd_i = tr.get_var_allsites(daily, 'mid_swc_interp', sites, startyear=startyr, endyear=endyr)
#rbd_i = rbd_i.resample( '1M', how='mean' )
# Write files to outpath
#rbd_i.to_csv(outpath + 'NMEG_monthly_midSWC.csv')

# Pull out deep
#rbd_i = tr.get_var_allsites(daily, 'deep_swc_interp', sites, startyear=startyr, endyear=endyr)
#rbd_i = rbd_i.resample( '1M', how='mean' )
# Write files to outpath
#rbd_i.to_csv(outpath + 'NMEG_monthly_deepSWC.csv')

