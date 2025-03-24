#!/usr/bin/env python
# coding: utf-8

# Stokes drift
# Computes Stokes drift from partitioned Stokes drift.

import sys
import os
import numpy as np
import xarray as xr
import pandas as pd
sys.path.append(os.path.join(os.pardir, 'gotmtool'))
from gotmtool import *
from gotmtool.stokesdrift import stokes_drift_usp
from tqdm import tqdm
from multiprocess import Pool

# Load data

gotmtool_config = os.path.join(os.pardir, 'gotmtool', '.gotm_env.yaml')
gotm_env = config_load(gotmtool_config)

inputstart = '20080601'
inputend = '20091231'
gotmdata = 'gotmdata_jra55do_20180920'
dlon = 4
dlat = 4
lat_start = -70
lat_end = 70
lon_start = 2
lon_end = 358
datadir = os.path.join(gotm_env['gotmdir_data'], 'gotm', 'gotmdata', gotmdata)
inputdir = os.path.join(gotm_env['gotmdir_data'], 'gotm', 'gotmdata', 'WAVEWATCH_JRA55-do')

caselist = os.listdir(datadir)

ds = xr.open_mfdataset(os.path.join(inputdir, 'ww3.200?_usp.nc'))

# Vertical grid

z1 = -np.linspace(0.5, 35.5, 36)
z2 = -np.linspace(40, 200, 17)
z = np.concatenate((np.array([0.0]), z1, z2))

# Compute and save Stokes drift

def compute_stokes_drift(cname):
    outputdir = os.path.join(datadir, cname)
    pfldata = os.path.join(outputdir, 'us_prof.dat')
    srfdata = os.path.join(outputdir, 'us_surface.dat')
    if (not os.path.exists(pfldata)) or (not os.path.exists(srfdata)):
        _, latstr, lonstr, _ = cname.split('_')
        rlat = float(latstr[3:])
        rlon = float(lonstr[3:])
        if rlon >= 180:
            rlon = rlon - 360.0
        dss = ds.sel(time=slice(inputstart,inputend), longitude=rlon, latitude=rlat)

        # time
        time = dss.time.values
        ntime = time.size
        # band center frequency
        freq = dss.f.values
        # partitioned Stokes drift
        ussp = dss.data_vars['ussp'].values
        vssp = dss.data_vars['vssp'].values

        # Compute Stokes drift
        ntime = time.size
        nz = z.size
        us = np.zeros([ntime, nz])
        vs = np.zeros([ntime, nz])
        for i in np.arange(ntime):
            us[i,:], vs[i,:] = stokes_drift_usp(z, freq, ussp[i,:], vssp[i,:])

        # Convert time from `numpy.datetime64` to `datetime.datetime`
        dttime = [pd.Timestamp(time[i]).to_pydatetime() for i in np.arange(ntime)]

        # Save Stokes drift to file
        dat_dump_pfl(dttime, z, [us, vs], pfldata)
        dat_dump_ts(dttime, [us[:,0], vs[:,0]], srfdata)

# Run in parallel and show the progress
max_pool = 8

with Pool(max_pool) as p:
    pool_outputs = list(
        tqdm(
            p.imap(compute_stokes_drift,
                   caselist),
            total=len(caselist)
        )
    )
