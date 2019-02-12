import os
import pathlib
import shutil

import pytest

from virtbuilder.utils import load_yaml


@pytest.fixture
def get_fixture():
    """ Return the path to a fixture. """

    module = pathlib.Path(__file__)
    fixtures_dir = module.parent / "fixtures"

    def _getter(filename):
        return fixtures_dir / filename

    return _getter


@pytest.fixture
def load_fixture(get_fixture):
    """ Load a fixture """

    def _loader(filename):
        path = get_fixture(filename)
        data = load_yaml(path)
        return data

    return _loader


# Support "slow" tests
# https://docs.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option
def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
