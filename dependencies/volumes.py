import nibabel as nib
import numpy as np
import subprocess


def reshape2Dto4D(signal2d, dims):

    signal4d = np.reshape(signal2d,
                          (dims[0], dims[1], dims[2], signal2d.shape[0]))

    return (signal4d)


def generate_header(dims, path):

    subprocess.run(
        '3dEmpty -nxyz {} {} {} -nt {} -prefix {}/{} -overwrite'.format(
            dims[0], dims[1], dims[2], dims[3], path, 'empty'),
        shell=True)


def read_header(path, filename):

    header_filename = '{}/{}'.format(path, filename)

    return (nib.load(header_filename).header)


def export_volume(vol, dims, path, filename, history):

    # Append nscans to dims
    dims = np.append(dims, vol.shape[0])

    # 2D to 4D
    vol_4d = reshape2Dto4D(vol, dims)

    # Generate header file
    generate_header(dims, path)

    # Read header file
    header = read_header(path, 'empty+orig.HEAD')

    print('Saving image...')
    img = nib.nifti1.Nifti1Image(vol_4d, None, header=header)
    img_filename = '{}/{}.nii.gz'.format(path, filename)
    nib.save(img, img_filename)
    print('Image {} saved.'.format(img_filename))

    # subprocess.run('3dcopy {} {} -overwrite'.format(img_filename,
    #                                                 img_filename),
    #                shell=True)

    if history is not None:
        print('Updating file history...')
        subprocess.run('3dNotes -h "{}" {}'.format(history, img_filename),
                       shell=True)
        print('File history updated.')
