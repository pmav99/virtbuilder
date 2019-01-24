import pathlib

from schema import Schema, And, Or, Use, Optional, SchemaError

from ..command import Command
from ...schemas import full_schema
from ...utils import load_yaml
from ... import api

_BUILD_HELP = """\
A wrapper around "virt-builder".

It reads a Virtual Machine (VM) image <c2>definition</> from a yaml file and creates it
using "<c1>virt-builder</>". If <c2>preview</> is defined, then the command is only
printed on StdOut.
"""


class BuildCommand(Command):
    """
    Build the image based on the provided definition.

    build
        {definition : The yaml file with the image configuration}
        {--preview : If set, the command will only be displayed on StdOut}
    """

    help = " ".join(_BUILD_HELP.splitlines()).strip()

    schema = Schema(
        {
            "definition": And(
                str,
                Use(pathlib.Path),
                lambda p: p.exists(),
                Use(load_yaml),
                full_schema.validate,
            ),
            "preview": And(bool),
        }
    )

    def handle(self):
        params = self.parse_parameters()
        self.line("")
        cmd = api.generate_build_command(params["definition"], singleline=False)
        self.line(cmd)
        if not params["preview"]:
            self.line("")
            return api.execute_cmd(cmd)
