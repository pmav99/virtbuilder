import pathlib

import pytest
from cleo.testers import CommandTester

# from virtbuilder.console.commands import BuildCommand
#
#
# @pytest.mark.slow
# def test_that_a_simple_image_can_be_created(get_fixture):
#     fixture = get_fixture("simple.yml")
#     cmd = BuildCommand()
#     tester = CommandTester(cmd)
#     tester.execute(fixture.as_posix())
#     # print(repr(tester.io.fetch_output()))
#     image = pathlib.Path("/tmp/simple.qcow2")
#     assert image.exists()
#     assert image.stat().st_size > 20000  # The image should be ~30MB
#     # cleanup
#     image.unlink()
