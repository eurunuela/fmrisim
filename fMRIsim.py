#!/usr/bin/python
import sys, argparse, os, socket, getpass, datetime
from dependencies.simulate import fMRIsim
import dependencies.volumes as vol
import numpy as np
import shutil


def main(argv):

    parser = argparse.ArgumentParser(description='fMRI data simulation')
    # parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Shows the list of possible commands and a brief description of each.')

    # Parameters for signal creation
    parser.add_argument(
        '--length',
        type=str,
        help=
        'Length of events to simulate ("short", "medium", "long" or "mix". Default="mix").',
        default='mix',
        nargs=1)
    parser.add_argument(
        '--nxyz',
        type=int,
        help='Number of voxels to simulate in X, Y and Z (default=1 1 1).',
        default=[1, 1, 1],
        nargs='+')
    parser.add_argument(
        '--duration',
        type=int,
        help='Duration in seconds of time series to simulate (default=400).',
        default=400,
        nargs=1)
    parser.add_argument('--tr',
                        type=float,
                        help='TR to simulate data with (default=2).',
                        default=2,
                        nargs=1)
    parser.add_argument('--nevents',
                        type=int,
                        help='Number of events to simulate (default=2).',
                        default=2,
                        nargs=1)
    parser.add_argument(
        '--gap',
        type=int,
        help='Number of minimum timepoints between events (default=5).',
        default=5,
        nargs=1)
    parser.add_argument(
        '--maxlength',
        type=int,
        help='Maximum number of timepoints for event length (default=None).',
        default=None,
        nargs=1)
    parser.add_argument(
        '--minlength',
        type=int,
        help='Minimum number of timepoints for event length (default=None).',
        default=None,
        nargs=1)
    parser.add_argument('--group', type=int, help='Number of voxels in each group of similar time series (default=nvoxels). It takes one value per group of voxels.', \
                        default=1, nargs='+')

    # Parameters for HRF matrix creation
    parser.add_argument(
        '--te',
        type=int,
        help=
        'Tuple with TE values (in ms) to simulate data with (default=None).',
        default=None,
        nargs='+')
    parser.add_argument(
        '--afni',
        help='Whether to use AFNI for HRF generation (default=False).',
        default=False,
        action='store_true')
    parser.add_argument(
        '--rmodel',
        type=str,
        help='Response model to use in AFNI\'s 3dDeconvolve (default="SMPG1").',
        default='SPMG1',
        nargs=1)

    # Noise
    parser.add_argument(
        '--tesla',
        type=int,
        help='Amount of Teslas to simulate (1.5, 3 or 7. Default=3).',
        default=3,
        nargs=1)
    parser.add_argument(
        '--no_noise',
        help='Whether to simulate data with no noise (default=False).',
        default=False,
        action='store_true')
    parser.add_argument(
        '--snr',
        type=float,
        help=
        'Amount of db to simulate (default=10.0). Mind that the default value is high., i.e. the amount of noise is very little.',
        default=10,
        nargs=1)

    parser.add_argument('--filename',
                        type=str,
                        help='Output filename (default="simulation").',
                        default='simulation',
                        nargs=1)
    parser.add_argument('--foldername',
                        type=str,
                        help='Output filename (default="data").',
                        default='data',
                        nargs=1)
    parser.add_argument(
        '--npy',
        help=
        'Whether to save files as .npy instead of nii.gz (default=False). npy data is 2D while NIFTI data is 4D.',
        default=False,
        action='store_true')

    args = parser.parse_args()

    if args.te is None:
        args.te = [1]

    sim = fMRIsim()

    if type(args.length) is list:
        sim.length = args.length[0]
    else:
        sim.length = args.length
    sim.nvoxels = np.prod(args.nxyz)
    dims = np.array(args.nxyz)
    if type(args.duration) is list:
        sim.dur = args.duration[0]
    else:
        sim.dur = args.duration
    if type(args.tr) is list:
        sim.tr = args.tr[0]
    else:
        sim.tr = args.tr
    if type(args.nevents) is list:
        sim.nevents = args.nevents[0]
    else:
        sim.nevents = args.nevents
    if type(args.gap) is list:
        sim.gap = args.gap[0]
    else:
        sim.gap = args.gap
    if type(args.maxlength) is list:
        sim.max_length = args.maxlength[0]
    else:
        sim.max_length = args.maxlength
    if type(args.minlength) is list:
        sim.min_length = args.minlength[0]
    else:
        sim.min_length = args.minlength
    sim.te = args.te
    sim.is_afni = args.afni
    sim.lop_hrf = args.rmodel
    if type(args.tesla) is list:
        sim.tesla = args.tesla[0]
    else:
        sim.tesla = args.tesla
    if type(args.db) is list:
        sim.db = args.snr[0]
    else:
        sim.db = args.snr
    if args.no_noise:
        sim.has_noise = False
    if sim.nvoxels == 1 and args.group == 1:
        sim.group = args.group
    elif sim.nvoxels > 1 and args.group == 1:
        sim.group = sim.nvoxels
    else:
        sim.group = args.group
    try:
        sim.ngroups = len(sim.group)
    except:
        sim.ngroups = 1

    sim.simulate()

    args_str = ' '.join(argv)
    history = '[{username}@{hostname}: {date}] python pySPFM.py {arguments}'.format(username=getpass.getuser(),\
                  hostname=socket.gethostname(), date=datetime.datetime.now().strftime('%c'), arguments=args_str)

    # Generate new folder
    if args.foldername.count('/') == 1:
        foldername = '{}/{}'.format(os.getcwd(), args.foldername)
    else:
        foldername = args.foldername

    # Check if temp directory exists
    if not os.path.exists(foldername):
        os.makedirs(foldername)  # Generate new dir
    else:
        shutil.rmtree(foldername)  # Remove dir for a clean start
        os.makedirs(foldername)  # Generate new dir

    # Saving simulations
    for te_idx in range(len(sim.te)):
        # Each of the TE data
        temp_sim = sim.simulation[te_idx * sim.nscans:(te_idx + 1) *
                                  sim.nscans, :].copy()
        vol.export_volume(
            temp_sim, dims, foldername,
            '{}_data_E0{}'.format(args.filename, str(te_idx + 1)), history)

        # Each of the TE BOLD data
        temp_bold = sim.bold[te_idx * sim.nscans:(te_idx + 1) *
                             sim.nscans, :].copy()
        vol.export_volume(
            temp_bold, dims, foldername,
            '{}_bold_E0{}'.format(args.filename, str(te_idx + 1)), history)

        # Each of the TE BOLD data
        temp_noise = sim.noise[te_idx * sim.nscans:(te_idx + 1) *
                               sim.nscans, :].copy()

        vol.export_volume(
            temp_noise, dims, foldername,
            '{}_noise_E0{}'.format(args.filename, str(te_idx + 1)), history)

    # Non TE dependent data
    vol.export_volume(sim.r2, dims, foldername, args.filename + '_r2', history)
    vol.export_volume(sim.innovation, dims, foldername,
                      args.filename + '_innovation', history)

    if args.npy:
        np.save('{}/{}_data'.format(foldername, args.filename),
                sim.simulation)  # Data
        np.save('{}/{}_bold'.format(foldername, args.filename),
                sim.bold)  # BOLD
        np.save('{}/{}_noise'.format(foldername, args.filename),
                sim.noise)  # Noise
        np.save('{}/{}_r2'.format(foldername, args.filename), sim.r2)  # R2
        np.save('{}/{}_innovation'.format(foldername, args.filename),
                sim.innovation)  # Innovation signal

    print('Simulated data generated! Your data is in: /{}'.format(foldername))


if __name__ == "__main__":
    main(sys.argv[1:])