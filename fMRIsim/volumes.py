import os
import subprocess

import nibabel as nib
import numpy as np


def reshape2Dto4D(signal2d, dims):

    signal4d = np.zeros((dims[0] * dims[1] * dims[2], signal2d.shape[0]))

    # Merges signal on mask indices with blank image
    for i in range(signal2d.shape[0]):
        signal4d[:, i] = signal2d[i, :]

    # Reshapes matrix from 2D to 4D double
    signal4d = np.reshape(signal4d, (dims[0], dims[1], dims[2], signal2d.shape[0]))

    return signal4d


def generate_header(dims, path):

    print(path)

    subprocess.run(
        "3dEmpty -nxyz {} {} {} -nt {} -prefix {}/{} -overwrite".format(
            dims[0], dims[1], dims[2], dims[3], path, "empty.nii.gz"
        ),
        shell=True,
    )

    print(os.listdir(path))


def read_header(path, filename):

    header_filename = os.path.join(path, filename)

    return nib.load(header_filename).header


def export_volume(vol_2d, dims, path, filename, history):

    #  Append nscans to dims
    dims = np.append(dims, vol_2d.shape[0])

    # 2D to 4D
    vol_4d = reshape2Dto4D(vol_2d, dims)

    #  Generate header file
    generate_header(dims, path)

    # Read header file
    header = read_header(path, "empty.nii.gz")

    print("Saving image...")
    img = nib.nifti1.Nifti1Image(vol_4d, None, header=header)
    img_filename = os.path.join(path, f"{filename}.nii.gz")
    nib.save(img, img_filename)
    print("Image {} saved.".format(img_filename))

    # subprocess.run('3dcopy {} {} -overwrite'.format(img_filename,
    #                                                 img_filename),
    #                shell=True)

    if history is not None:
        print("Updating file history...")
        subprocess.run('3dNotes -h "{}" {}'.format(history, img_filename), shell=True)
        print("File history updated.")
