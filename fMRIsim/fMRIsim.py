#!/usr/bin/python
import os
import shutil

import numpy as np

import fMRIsim.volumes as vol
from fMRIsim.simulate import fMRIsim


def fMRIsim_workflow(
    out_file="simulation",
    out_dir="data",
    length="mix",
    nxyz=[1, 1, 1],
    duration=400,
    tr=2,
    te=None,
    nevents=2,
    gap=10,
    maxlength=None,
    minlength=None,
    group=None,
    afni=False,
    hrfmodel="SPMG1",
    hrfpath=None,
    tesla=3,
    no_noise=False,
    snr=10,
    motpath=None,
    npy=False,
    history="",
):

    if te is None:
        te = [1]

    sim = fMRIsim()
    sim.length = length
    sim.nvoxels = np.prod(nxyz)
    sim.dur = duration
    sim.tr = tr
    sim.nevents = nevents
    sim.gap = gap
    sim.max_length = maxlength
    sim.min_length = minlength
    sim.te = te
    sim.is_afni = afni
    sim.lop_hrf = hrfmodel
    sim.hrf_path = hrfpath
    sim.tesla = tesla
    sim.db = snr
    sim.mot_path = motpath
    if no_noise:
        sim.has_noise = False
    if sim.nvoxels == 1 and group is None:
        sim.group = 1
    elif sim.nvoxels > 1 and group is None:
        sim.group = sim.nvoxels
    else:
        sim.group = group
    try:
        sim.ngroups = len(sim.group)
    except:
        sim.ngroups = 1

    sim.simulate()

    dims = np.array(nxyz)

    # Check if temp directory exists
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)  # Generate new dir
    else:
        shutil.rmtree(out_dir)  # Remove dir for a clean start
        os.mkdir(out_dir)  # Generate new dir

    # Saving simulations
    for te_idx in range(len(sim.te)):
        # Each of the TE data
        temp_sim = sim.simulation[
            te_idx * sim.nscans : (te_idx + 1) * sim.nscans, :
        ].copy()
        vol.export_volume(
            temp_sim,
            dims,
            out_dir,
            "{}_data_E0{}".format(out_file, str(te_idx + 1)),
            history,
        )

        #  Each of the TE BOLD data
        temp_bold = sim.bold[te_idx * sim.nscans : (te_idx + 1) * sim.nscans, :].copy()
        vol.export_volume(
            temp_bold,
            dims,
            out_dir,
            "{}_bold_E0{}".format(out_file, str(te_idx + 1)),
            history,
        )

        #  Each of the TE BOLD data
        temp_noise = sim.noise[
            te_idx * sim.nscans : (te_idx + 1) * sim.nscans, :
        ].copy()

        vol.export_volume(
            temp_noise,
            dims,
            out_dir,
            "{}_noise_E0{}".format(out_file, str(te_idx + 1)),
            history,
        )

    #  Non TE dependent data
    vol.export_volume(sim.r2, dims, out_dir, out_file + "_r2", history)
    vol.export_volume(sim.innovation, dims, out_dir, out_file + "_innovation", history)

    if npy:
        np.save(os.path.join(out_dir, f"{out_file}_data"), sim.simulation)  # Data
        np.save(os.path.join(out_dir, f"{out_file}_bold"), sim.bold)  # BOLD
        np.save(os.path.join(out_dir, f"{out_file}_noise"), sim.noise)  # Noise
        np.save(os.path.join(out_dir, f"{out_file}_r2"), sim.r2)  # R2
        np.save(
            os.path.join(out_dir, f"{out_file}_innovation"), sim.innovation
        )  # Innovation signal

    print("Simulated data generated! Your data is in: /{}".format(out_dir))
