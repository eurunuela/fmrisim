import os
import numpy as np

from fMRIsim import hrf_matrix


def test_hrf_linear():
    tr = 2
    p = [6, 16, 1, 1, 6, 0, 32]
    hrf = hrf_matrix.hrf_linear(tr, p)

    result = np.array([5.40361636e-12, 2.88715266e-01, 1.25032756e+00, 1.28379679e+00,
        7.20794654e-01, 2.56375439e-01, 5.40361636e-03, -1.02083200e-01,
       -1.24423263e-01, -1.02848828e-01, -6.84254253e-02, -3.88356248e-02,
       -1.94129750e-02, -8.73336515e-03, -3.59309106e-03, -1.36891158e-03,
       -4.87798160e-04])

    assert np.allclose(hrf, result)


def test_hrf_afni():

    tr = 2
    hrfmodel = "SPMG1"
    hrf = hrf_matrix.hrf_afni(tr, hrfmodel)

    result = np.array([ 0, 0.0360894, 0.156291, 0.160475, 0.0900993,
        0.0320469, 0.00067546, -0.0127604, -0.0155529, -0.0128561,
       -0.00855318, -0.00485445, -0.00242662])

    assert np.allclose(hrf, result)


def test_HRFMatrix():

    hrf = hrf_matrix.HRFMatrix()

    assert hrf.TR == 2
    assert hrf.TE is None
    assert hrf.nscans == 200
    assert hrf.r2only == 1
    assert hrf.is_afni is True
    assert hrf.lop_hrf == "SPMG1"
    assert hrf.hrf_path is None
    assert hrf.has_integrator is False

    hrf.generate_hrf()

    result = np.array([ 0, 0.0360894, 0.156291, 0.160475, 0.0900993,
        0.0320469, 0.00067546, -0.0127604, -0.0155529, -0.0128561,
       -0.00855318, -0.00485445, -0.00242662])

    assert np.allclose(hrf.hrf[:len(result), 0], result)
    assert np.max(hrf.hrf_norm) == 1