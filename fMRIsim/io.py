"""I/O for fMRIsim."""
import logging
import os
import subprocess

import nibabel as nib
import numpy as np

LGR = logging.getLogger(__name__)


def reshape2Dto4D(signal2d, dims):
    """[summary].

    Parameters
    ----------
    signal2d : [type]
        [description]
    dims : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    signal4d = np.zeros((dims[0] * dims[1] * dims[2], signal2d.shape[0]))

    # Merges signal on mask indices with blank image
    for i in range(signal2d.shape[0]):
        signal4d[:, i] = signal2d[i, :]

    # Reshapes matrix from 2D to 4D double
    signal4d = np.reshape(signal4d, (dims[0], dims[1], dims[2], signal2d.shape[0]))

    return signal4d


def generate_header(dims, path):
    """[summary].

    Parameters
    ----------
    dims : [type]
        [description]
    path : [type]
        [description]
    """
    subprocess.run(
        f"3dEmpty -nxyz {dims[0]} {dims[1]} {dims[2]} -nt {dims[3]} -prefix "
        f"{path}/{'empty'} -overwrite",
        shell=True,
    )


def read_header(path, filename):
    """[summary].

    Parameters
    ----------
    path : [type]
        [description]
    filename : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    header_filename = os.path.join(path, filename)

    return nib.load(header_filename).header


def export_volume(vol_2d, dims, path, filename, history):
    """[summary].

    Parameters
    ----------
    vol_2d : [type]
        [description]
    dims : [type]
        [description]
    path : [type]
        [description]
    filename : [type]
        [description]
    history : [type]
        [description]
    """
    #  Append nscans to dims
    dims = np.append(dims, vol_2d.shape[0])

    # 2D to 4D
    vol_4d = reshape2Dto4D(vol_2d, dims)

    #  Generate header file
    generate_header(dims, path)

    # Read header file
    header = read_header(path, "empty+orig.HEAD")

    LGR.info("Saving image...")
    img = nib.nifti1.Nifti1Image(vol_4d, None, header=header)
    img_filename = os.path.join(path, f"{filename}.nii.gz")
    nib.save(img, img_filename)
    LGR.info(f"Image {img_filename} saved.")

    # subprocess.run('3dcopy {} {} -overwrite'.format(img_filename,
    #                                                 img_filename),
    #                shell=True)

    if history is not None:
        LGR.info("Updating file history...")
        subprocess.run(f'3dNotes -h "{history}" {img_filename}', shell=True)
        LGR.info("File history updated.")
