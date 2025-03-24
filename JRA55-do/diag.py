#!/usr/bin/env python
# coding: utf-8

import sys
import os
import numpy as np
sys.path.append(os.path.join(os.pardir, 'gotmtool'))
from gotmtool import *
from gotmtool.map import *
from gotmtool.diags import get_mld_deltaR, get_mld_deltaT

gotmtool_config = os.path.join(os.pardir, 'gotmtool', '.gotm_env.yaml')
gotm_env = config_load(gotmtool_config)

casename = 'JRA55-do_Global_dampV5d_3h'
dz = 1
dt = 600
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
# turbmethod = 'KPP-CVMix'
# turbmethod = 'KPPLT-LF17'
turbmethod = 'StokesMOST'

outputfile = 'data_map_mld_deltaR_mean_{:s}.npz'.format(turbmethod)

def get_gotmmap_mld_deltaR(rundir):
    caselist = os.listdir(rundir)
    ndata = len(caselist)
    data = np.zeros(ndata)
    lon = np.zeros(ndata)
    lat = np.zeros(ndata)
    tenp = int(ndata/10)
    for i, cname in enumerate(caselist):
        if i%tenp == 0:
            print(' - Progress: {:6.2f} %'.format(i//tenp*10))
        if os.path.exists(os.path.join(rundir, cname, 'gotm_out.nc')):
            sim = Simulation(path=os.path.join(rundir, cname), dataname='gotm_out.nc')
            ds = sim.load_data()
            rho = ds.data_vars['rho_p']
            mld = get_mld_deltaR(rho)
            # data[i] = mld.isel(time=0)
            mld = mld.where(mld<np.abs(np.min(ds.z)))
            data[i] = mld.mean(dim='time', skipna=True)
            lon[i] = ds.lon
            lat[i] = ds.lat
    gmobj = GOTMMap(data=data, lon=lon, lat=lat, name='mld_deltaR', units='m')
    return gmobj

for date_start in simtime.keys():
    date_end = simtime[date_start]
    setup = 'VR{:d}m_DT{:d}s_{:s}-{:s}'.format(int(dz), int(dt), date_start, date_end)
    print(setup)
    outputdir = os.path.join(gotm_env['gotmdir_figure'], 'data', casename, setup)
    rundir = os.path.join(gotm_env['gotmdir_run'], casename, setup, turbmethod)
    os.makedirs(outputdir, exist_ok=True)
    gmobj = get_gotmmap_mld_deltaR(rundir)
    ofile = os.path.join(outputdir, outputfile)
    gmobj.save(ofile)
