import os

import pytest

from fMRIsim.fMRIsim import fMRIsim_workflow


def test_integration(skip_integration, testpath):
    if skip_integration:
        pytest.skip("Skipping integration test")

    fMRIsim_workflow(out_dir=testpath, nxyz=[2, 2, 2], afni=True)

    name_ext_list = ["bold", "data", "noise"]
    for ext in name_ext_list:
        assert os.path.isfile(os.path.join(testpath, f"simulation_{ext}_E01.nii.gz"))

    name_ext_list = ["innovation", "r2"]
    for ext in name_ext_list:
        assert os.path.isfile(os.path.join(testpath, f"simulation_{ext}.nii.gz"))
