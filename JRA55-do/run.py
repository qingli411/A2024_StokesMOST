#!/usr/bin/env python
# coding: utf-8

# # JRA55-do forced simulations
#
# This notebook runs a set of [GOTM](https://gotm.net/) simulations within each $4^\circ \times 4^\circ$ box over the global ocean between 72$^\circ$ N/S using realistic surface forcing and ocean surface wave information from [JRA55-do](https://climate.mri-jma.go.jp/pub/ocean/JRA55-do/) and JRA55-do forced WAVEWATCH III simulations. Initial conditions were taken from [Argo](https://argo.ucsd.edu/) profiles. See [Li et al., 2019](https://doi.org/10.1029/2019MS001810) for more details.

import sys
import os
import copy
import numpy as np
import matplotlib.pyplot as plt
sys.path.append(os.path.join(os.pardir, 'gotmtool'))
from gotmtool import *


# ## Create a model
# Create a model with environment file `gotmtool/.gotm_env.yaml`, which is created by `gotm_env_init.py`.

m = Model(name='JRA55-do_Global_dampV5d_3h', environ=os.path.join(os.pardir, 'gotmtool', '.gotm_env.yaml'))


# Take a look at what are defined in the environment file.

for key in m.environ:
    print('{:>15s}: {}'.format(key, m.environ[key]) )


# ## Build the model

m.build()


# ## Configuration
# Initialize the GOTM configuration

cfg = m.init_config()


# Update the configuration

# setup
title = 'JRA55-do'
nlev = 500
depth = 500
dt = 600
dz = depth/nlev

inputstart = '20080601'
inputend = '20091231'
gotmdata = 'gotmdata_jra55do_20180920'
dlon = 4
dlat = 4
lat_start = -70
lat_end = 70
lon_start = 2
lon_end = 358
simtime = {
    '20080601': '20080630',
    '20080701': '20080731',
    '20080801': '20080831',
    '20080901': '20080930',
    '20081001': '20081031',
    '20081101': '20081130',
    '20081201': '20081231',
    '20090101': '20090131',
    '20090201': '20090228',
    '20090301': '20090331',
    '20090401': '20090430',
    '20090501': '20090531',
}
datadir = os.path.join(m.environ['gotmdir_data'], 'gotm', 'gotmdata', gotmdata)

# config
cfg['title'] = title
cfg['location']['depth'] = depth
cfg['time']['dt']    = dt
cfg['grid']['nlev']  = nlev

# output
cfg['output'] = {}
cfg['output']['gotm_out'] = {}
cfg['output']['gotm_out']['use'] = True
cfg['output']['gotm_out']['title'] = title
cfg['output']['gotm_out']['k1_stop'] = nlev+1
cfg['output']['gotm_out']['k_stop'] = nlev
cfg['output']['gotm_out']['time_unit'] = 'hour'
cfg['output']['gotm_out']['time_step'] = 3
# cfg['output']['gotm_out']['variables'] = [{'source':'temp'}, {'source':'salt'}]
cfg['output']['gotm_out']['variables'] = [{'source': '*'}]

# forcing
cfg['temperature']['method'] = 'file'
cfg['salinity']['method'] = 'file'
cfg['surface']['fluxes']['method'] = 'fairall'
cfg['surface']['u10']['method'] = 'file'
cfg['surface']['u10']['column'] = 1
cfg['surface']['v10']['method'] = 'file'
cfg['surface']['v10']['column'] = 2
cfg['surface']['airp']['method'] = 'file'
cfg['surface']['airp']['column'] = 3
cfg['surface']['airp']['scale_factor'] = 100.
cfg['surface']['airt']['method'] = 'file'
cfg['surface']['airt']['column'] = 4
cfg['surface']['hum']['method'] = 'file'
cfg['surface']['hum']['column'] = 5
cfg['surface']['hum']['type'] = 'specific'
cfg['surface']['swr']['method'] = 'file'
cfg['surface']['longwave_radiation']['method'] = 'clark'
cfg['surface']['precip']['method'] = 'file'
cfg['surface']['precip']['scale_factor'] = 1e-3
cfg['surface']['calc_evaporation'] = False

# waves
cfg['waves']['Hs']['method'] = 'file'
cfg['waves']['Hs']['column'] = 1
cfg['waves']['stokes_drift']['us0']['method'] = 'file'
cfg['waves']['stokes_drift']['us0']['column'] = 1
cfg['waves']['stokes_drift']['vs0']['method'] = 'file'
cfg['waves']['stokes_drift']['vs0']['column'] = 2
cfg['waves']['stokes_drift']['us']['method'] = 'file'
cfg['waves']['stokes_drift']['us']['column'] = 1
cfg['waves']['stokes_drift']['vs']['method'] = 'file'
cfg['waves']['stokes_drift']['vs']['column'] = 2

# relax velocity to zero with time scale of 5 days
cfg['velocities']['u']['method'] = 'constant'
cfg['velocities']['u']['constant_value'] = 0.0
cfg['velocities']['v']['method'] = 'constant'
cfg['velocities']['v']['constant_value'] = 0.0
cfg['velocities']['relax']['tau'] = 432000

# water type (Jerlov 1)
cfg['light_extinction']['method'] = 'jerlov-i'

# EOS -- use linear
cfg['equation_of_state']['method'] = 'linear_custom'
cfg['equation_of_state']['linear']['T0'] = 10.0
cfg['equation_of_state']['linear']['S0'] = 35.0
cfg['equation_of_state']['linear']['alpha'] = 1.66e-4
cfg['equation_of_state']['linear']['beta'] = 7.6e-4
cfg['equation_of_state']['rho0'] = 1027.0
cfg['equation_of_state']['linear']['cp'] = 3985.0


cfgs = []
labels = []


# caselist = ['JRA55-do_LAT-70_LON270_20080601-20091231']
caselist = os.listdir(datadir)
ncase = len(caselist)
tenp = int(ncase/10)
print('Preparing config files...')
for i, case in enumerate(caselist):
    if i%tenp == 0:
        print(' - Progress: {:6.2f} %'.format(i//tenp*10))
    _, latstr, lonstr, _ = case.split('_')
    casename = '{:s}_{:s}_{:s}'.format(title, latstr, lonstr)
    rlat = float(latstr[3:])
    rlon = float(lonstr[3:])
    if rlon >= 180:
        rlon = rlon - 360.0
    inputdir = os.path.join(datadir, case)
    cfg['location']['name'] = case
    cfg['location']['latitude'] = rlat
    cfg['location']['longitude'] = rlon
    cfg['surface']['u10']['file'] = os.path.join(inputdir, 'meteo_file.dat')
    cfg['surface']['v10']['file'] = os.path.join(inputdir, 'meteo_file.dat')
    cfg['surface']['airp']['file'] = os.path.join(inputdir, 'meteo_file.dat')
    cfg['surface']['airt']['file'] = os.path.join(inputdir, 'meteo_file.dat')
    cfg['surface']['hum']['file'] = os.path.join(inputdir, 'meteo_file.dat')
    cfg['surface']['swr']['file'] = os.path.join(inputdir, 'swr_file.dat')
    cfg['surface']['precip']['file'] = os.path.join(inputdir, 'precip_file.dat')
    cfg['waves']['Hs']['file'] = os.path.join(inputdir, 'wave_file.dat')
    cfg['waves']['stokes_drift']['us0']['file'] = os.path.join(inputdir, 'us_surface.dat')
    cfg['waves']['stokes_drift']['vs0']['file'] = os.path.join(inputdir, 'us_surface.dat')
    cfg['waves']['stokes_drift']['us']['file'] = os.path.join(inputdir, 'us_prof.dat')
    cfg['waves']['stokes_drift']['vs']['file'] = os.path.join(inputdir, 'us_prof.dat')
    for date_start in simtime.keys():
        date_end = simtime[date_start]
        tprof_file = os.path.join(inputdir, 'tprof_file_{:s}.dat'.format(date_start))
        sprof_file = os.path.join(inputdir, 'sprof_file_{:s}.dat'.format(date_start))
        if os.path.exists(tprof_file) and os.path.exists(sprof_file) and os.path.getsize(tprof_file) != 0 and os.path.getsize(sprof_file) != 0:
            setup = 'VR{:d}m_DT{:d}s_{:s}-{:s}'.format(int(dz), int(dt), date_start, date_end)
            cfg['time']['start'] = '{:s}-{:s}-{:s} 00:00:00'.format(date_start[0:4],date_start[4:6],date_start[6:8])
            cfg['time']['stop']  = '{:s}-{:s}-{:s} 23:59:59'.format(date_end[0:4],date_end[4:6],date_end[6:8])
            cfg['temperature']['file'] = tprof_file
            cfg['salinity']['file'] = sprof_file
            # turbmethods
            cfg['turbulence']['turb_method'] = 'cvmix'
            # cfg['cvmix']['surface_layer']['langmuir_method'] = 'none'
            # cfgs.append(copy.deepcopy(cfg))
            # labels.append(os.path.join(setup, 'KPP-CVMix', casename))
            # cfg['cvmix']['surface_layer']['langmuir_method'] = 'lf17'
            # cfgs.append(copy.deepcopy(cfg))
            # labels.append(os.path.join(setup, 'KPPLT-LF17', casename))
            cfg['cvmix']['surface_layer']['langmuir_method'] = 'none'
            cfg['cvmix']['surface_layer']['use_Stokes_MOST'] = True
            cfg['cvmix']['surface_layer']['check_MonOb_length'] = True
            cfg['cvmix']['surface_layer']['CVt2'] = 1.0
            cfgs.append(copy.deepcopy(cfg))
            labels.append(os.path.join(setup, 'StokesMOST', casename))


# ## Run the model

print('Running...')
m.run_batch(configs=cfgs, labels=labels, nproc=32)

