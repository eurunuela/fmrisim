import os
import pytest
from fMRIsim.fMRIsim import fMRIsim_workflow


def test_integration(skip_integration):
    if skip_integration:
        pytest.skip("Skipping integration test")

    fMRIsim_workflow(nxyz=[2, 2, 2])

    test_dir = os.getcwd()
    data_dir = os.path.join(test_dir, 'data')
    assert os.path.isdir(data_dir)

    name_ext_list = ['bold', 'data', 'noise']
    for ext in name_ext_list:
        assert os.path.isfile(os.path.join(data_dir, f'simulation_{ext}_E01.nii.gz'))

    name_ext_list = ['innovation', 'r2']
    for ext in name_ext_list:
        assert os.path.isfile(os.path.join(data_dir, f'simulation_{ext}.nii.gz'))