import pathlib

from schema import Schema, And, Or, Use, Optional, SchemaError

from ..command import Command
from ...utils import load_yaml
from ... import api

_BUILD_HELP = """\
A wrapper around "virt-builder". It

Reads a Virtual Machine (VM) <c2>configuration</> from a json file and creates a VM
using "<c1>virt-builder</>". If <c2>preview</> is defined, then the command is only
printed on stdout.
"""


class BuildCommand(Command):
    """
    Build the image based on the provided configuration

    build
        {config : The yaml file with the image configuration}
        {--preview : If set, virt-builder will not be executed}
    """

    help = " ".join(_BUILD_HELP.splitlines()).strip()

    schema = Schema(
        {
            "configuration": And(
                str, Use(pathlib.Path), lambda p: p.exists(), Use(load_yaml)
            ),
            "preview": And(bool),
        }
    )

    def handle(self):
        params = self.parse_parameters()
        self.line("")
        cmd = api.generate_command_from_template(
            "virt_builder.j2", params.configuration
        )
        self.line(cmd)
        if not params.preview:
            self.line("")
            return api.execute_cmd(cmd)
