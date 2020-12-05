import glob
import os
import subprocess

import pytest

from fMRIsim import _version


def check_string(str_container, str_to_find, str_expected, is_num=True):
    idx = [
        log_idx
        for log_idx, log_str in enumerate(str_container)
        if str_to_find in log_str
    ]
    str_found = str_container[idx[0]]
    if is_num:
        num_found = re.findall(r"[-+]?\d*\.\d+|\d+", str_found)
        return str_expected in num_found
    else:
        return str_expected in str_found


def test_integration(skip_integration, testpath):
    if skip_integration:
        pytest.skip("Skipping integration test")

    # fMRIsim_workflow(out_dir=testpath, nxyz=[2, 2, 2], afni=True, npy=True)
    command = f"fMRIsim -d {testpath} -nxyz {'2 2 2'} -afni -npy"
    subprocess.run(command, shell=True, check=True)

    # Read logger file
    logger_file = glob.glob(os.path.join(testpath, "fMRIsim*"))[0]
    with open(logger_file) as logger_info:
        logger_info = logger_info.readlines()

    # Get version info
    version_number = _version.get_versions()["version"]
    assert check_string(logger_info, "fMRIsim version", version_number, is_num=False)

    name_ext_list = ["bold", "data", "noise"]
    for ext in name_ext_list:
        assert os.path.isfile(os.path.join(testpath, f"simulation_{ext}_E01.nii.gz"))

    name_ext_list = ["innovation", "r2"]
    for ext in name_ext_list:
        assert os.path.isfile(os.path.join(testpath, f"simulation_{ext}.nii.gz"))

    name_ext_list = ["innovation", "r2", "bold", "data", "noise"]
    for ext in name_ext_list:
        assert os.path.isfile(os.path.join(testpath, f"simulation_{ext}.npy"))
