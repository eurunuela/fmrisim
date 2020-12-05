"""Main."""
import datetime
import logging
import os
import shutil

import numpy as np

from fMRIsim import _version
import fMRIsim.io as vol
from fMRIsim.simulate import fMRIsim

LGR = logging.getLogger(__name__)


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
    """[summary].

    Parameters
    ----------
    out_file : str, optional
        [description], by default "simulation"
    out_dir : str, optional
        [description], by default "data"
    length : str, optional
        [description], by default "mix"
    nxyz : list, optional
        [description], by default [1, 1, 1]
    duration : int, optional
        [description], by default 400
    tr : int, optional
        [description], by default 2
    te : [type], optional
        [description], by default None
    nevents : int, optional
        [description], by default 2
    gap : int, optional
        [description], by default 10
    maxlength : [type], optional
        [description], by default None
    minlength : [type], optional
        [description], by default None
    group : [type], optional
        [description], by default None
    afni : bool, optional
        [description], by default False
    hrfmodel : str, optional
        [description], by default "SPMG1"
    hrfpath : [type], optional
        [description], by default None
    tesla : int, optional
        [description], by default 3
    no_noise : bool, optional
        [description], by default False
    snr : int, optional
        [description], by default 10
    motpath : [type], optional
        [description], by default None
    npy : bool, optional
        [description], by default False
    history : str, optional
        [description], by default ""
    """
    if type(out_dir) is list:
        out_dir = out_dir[0]

    # Check if temp directory exists
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)  # Generate new dir
    else:
        shutil.rmtree(out_dir)  # Remove dir for a clean start
        os.mkdir(out_dir)  # Generate new dir

    # Create logfile name
    basename = 'fMRIsim_'
    extension = 'tsv'
    isotime = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
    logname = os.path.join(out_dir, (basename + isotime + '.' + extension))

    # Set logging format
    log_formatter = logging.Formatter(
        '%(asctime)s\t%(name)-12s\t%(levelname)-8s\t%(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')

    # Set up logging file and open it for writing
    log_handler = logging.FileHandler(logname)
    log_handler.setFormatter(log_formatter)
    sh = logging.StreamHandler()

    logging.basicConfig(level=logging.INFO,
                        handlers=[log_handler, sh], format='%(levelname)-10s %(message)s')

    version_number = _version.get_versions()['version']
    LGR.info(f'Currently running fMRIsim version {version_number}')

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
    if type(sim.group) is list:
        sim.ngroups = len(sim.group)
    else:
        sim.ngroups = 1

    sim.simulate()

    dims = np.array(nxyz)

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

    LGR.info(f"Simulated data generated! Your data is in: {out_dir}")
