import os
import pathlib
import shutil

import pytest

from virtbuilder.utils import load_yaml


@pytest.fixture
def data_path(tmp_path, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    module = pathlib.Path(request.module.__file__)
    filename = module.stem
    fixture_dir = module.parent / filename
    if fixture_dir.is_dir():
        data_path = tmp_path / filename
        shutil.copytree(fixture_dir, data_path)
    else:
        data_path = tmp_path
    return data_path


@pytest.fixture
def yaml_loader(data_path):
    def _loader(filename):
        yml_file = data_path / filename
        print(yml_file)
        if yml_file.exists():
            return load_yaml(yml_file)
        else:
            raise ValueError(f"There is no {stem} in {data_path}")

    return _loader
