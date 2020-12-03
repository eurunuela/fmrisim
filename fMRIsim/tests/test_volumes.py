import numpy as np

from fMRIsim import volumes as vol


def test_reshape2Dto4D():
    dims = (3, 3, 3, 50)
    signal2d = np.random.rand(50, 3 * 3 * 3)
    signal4d = vol.reshape2Dto4D(signal2d, dims)

    assert signal4d.shape == dims
