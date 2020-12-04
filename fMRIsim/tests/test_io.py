from nibabel import test
import numpy as np
import os
import subprocess

from fMRIsim import io


def test_reshape2Dto4D():
    dims = (3, 3, 3, 50)
    signal2d = np.random.rand(50, 27)
    signal4d = io.reshape2Dto4D(signal2d, dims)

    assert signal4d.shape == dims


def test_generate_header(testpath):
    dims = (3, 3, 3, 50)

    io.generate_header(dims, testpath)

    out_file = os.path.join(testpath, "empty+orig.HEAD")
    assert os.path.isfile(out_file)

    nvoxels = subprocess.check_output(
        f"3dinfo -nijk {out_file}", shell=True, universal_newlines=True
    ).splitlines()

    assert int(nvoxels[0]) == np.prod(dims[:3])

    ntime = subprocess.check_output(
        f"3dinfo -nt {out_file}", shell=True, universal_newlines=True
    ).splitlines()

    assert int(ntime[0]) == np.prod(dims[3])


def test_read_header(testpath):

    header_file = os.path.join(testpath, "empty+orig.HEAD")

    if not os.path.isfile(header_file):
        io.generate_header((3, 3, 3, 50), header_file)

    header = io.read_header(testpath, "empty+orig.HEAD")

    assert header.get_data_shape() == (3, 3, 3, 50)


def test_export_volume(testpath):

    vol_2d = np.random.rand(50, 27)
    dims = (3, 3, 3, 50)
    filename = "test.nii.gz"
    history = "Export volume unit test."
    io.export_volume(vol_2d, dims, testpath, "test", history)

    out_file = os.path.join(testpath, filename)
    assert os.path.isfile(out_file)

    info = subprocess.check_output(f"3dinfo {os.path.join(testpath, filename)}", shell=True, universal_newlines=True)
    assert history in info

    nvoxels = subprocess.check_output(
        f"3dinfo -nijk {out_file}", shell=True, universal_newlines=True
    ).splitlines()

    assert int(nvoxels[0]) == np.prod(dims[:3])

    ntime = subprocess.check_output(
        f"3dinfo -nt {out_file}", shell=True, universal_newlines=True
    ).splitlines()

    assert int(ntime[0]) == np.prod(dims[3])