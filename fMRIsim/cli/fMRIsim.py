import argparse
import datetime
import getpass
import socket

from fMRIsim import fMRIsim


def _get_parser():
    """
    Parse command line inputs for aroma.

    Returns
    -------
    parser.parse_args() : argparse dict
    """
    parser = argparse.ArgumentParser(
        description=(
            "Python package to simulate fMRI data."
        )
    )

    # Optional options
    optoptions = parser.add_argument_group("Optional arguments")
    optoptions.add_argument(
        "-o",
        "-out",
        dest="out_file",
        default="simulation",
        help=(
            "Name of the output file (default='simulation')."
        ),
        type=str,
        nargs=1
    )
    optoptions.add_argument(
        "-d",
        "-dir",
        dest="out_dir",
        default="data",
        help=(
            "Path to the output directory (default='data')."
        ),
        type=str,
        nargs=1
    )
    optoptions.add_argument(
        "-length",
        dest="length",
        default="mix",
        help=(
            "Length of events to simulate ('short', 'medium', 'long' or 'mix'). Default is 'mix'."
        ),
        type=str,
        nargs=1
    )
    optoptions.add_argument(
        "-nxyz",
        dest="nxyz",
        default=[1, 1, 1],
        help=(
            "Number of voxels to simulate in X, Y and Z (it must be a list of integers). Default is 1 1 1."
        ),
        type=int,
        nargs='+'
    )
    optoptions.add_argument(
        "-duration",
        dest="duration",
        default=400,
        help=(
            "Duration in seconds of time series to simulate (default=400). It must be an integer."
        ),
        type=int,
        nargs=1
    )
    optoptions.add_argument(
        "-tr",
        dest="tr",
        default=2,
        help=(
            "TR in seconds (default=2). Accepts floats."
        ),
        type=float,
        nargs=1
    )
    optoptions.add_argument(
        "-te",
        dest="te",
        default=None,
        help=(
            "List with TE values (in ms) to simulate data with (default=None)."
        ),
        type=float,
        nargs='+'
    )
    optoptions.add_argument(
        "-n",
        "-nevents",
        dest="nevents",
        default=2,
        help=(
            "Number of neuronal events to simulate (default=2)."
        ),
        type=int,
        nargs=1
    )
    optoptions.add_argument(
        "-gap",
        dest="gap",
        default=10,
        help=(
            "Number of minimum TRs between events (default=10)."
        ),
        type=int,
        nargs=1
    )
    optoptions.add_argument(
        "-maxlength",
        dest="maxlength",
        default=None,
        help=(
            "Maximum number of TRs for event length (default=None)."
        ),
        type=int,
        nargs=1
    )
    optoptions.add_argument(
        "-minlength",
        dest="minlength",
        default=None,
        help=(
            "Minimum number of TRs for event length (default=None)."
        ),
        type=int,
        nargs=1
    )
    optoptions.add_argument(
        "-group",
        dest="group",
        default=None,
        help=(
            "List with the number of voxels in each group of similar time series "
            "(default=None). It takes one value per group of voxels."
        ),
        type=int,
        nargs='+'
    )
    optoptions.add_argument(
        "-afni",
        dest="afni",
        action="store_true",
        help=(
            "Whether to use AFNI for HRF generation (default=False)."
        ),
        default=False,
    )
    optoptions.add_argument(
        "-hrfmodel",
        dest="hrfmodel",
        help=(
            "HRF model to use in AFNI\'s 3dDeconvolve (default='SMPG1')."
        ),
        default="SPMG1",
        type=str,
        nargs=1
    )
    optoptions.add_argument(
        "-hrfpath",
        dest="hrfpath",
        help=(
            "Path to the custom HRF model to use in AFNI\'s 3dDeconvolve (default=None)."
        ),
        default=None,
        type=str,
        nargs=1
    )
    optoptions.add_argument(
        "-t",
        "-tesla",
        dest="tesla",
        help=(
            "Amount of Teslas to simulate (1.5, 3 or 7). Default is 3."
        ),
        default=3,
        type=float,
        nargs=1
    )
    optoptions.add_argument(
        "-no_noise",
        dest="no_noise",
        action="store_true",
        help=(
            "Whether to simulate data with no noise (default=False)."
        ),
        default=False,
    )
    optoptions.add_argument(
        "-snr",
        dest="snr",
        help=(
            "Amount of db to simulate (default=10.0)."
        ),
        default=10,
        type=float,
        nargs=1
    )
    optoptions.add_argument(
        "-motpath",
        dest="motpath",
        help=(
            "Path to the motion parameter txt file (default=None)."
        ),
        default=None,
        type=str,
        nargs=1
    )
    optoptions.add_argument(
        "-npy",
        dest="npy",
        action="store_true",
        help=(
            "Whether to save files as .npy (default=False). npy data is 2D while NIFTI data is 4D."
        ),
        default=False,
    )

    return parser


def _main(argv=None):
    """Entry point for aroma CLI."""
    options = _get_parser().parse_args(argv)
    args_str = str(options)[9:]
    history_str = '[{username}@{hostname}: {date}] fMRIsim with {arguments}'.format(username=getpass.getuser(),\
                    hostname=socket.gethostname(), date=datetime.datetime.now().strftime('%c'), arguments=args_str)

    kwargs = vars(options)
    kwargs['history'] = history_str


if __name__ == "__main__":
    _main()
