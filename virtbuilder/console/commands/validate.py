import pathlib

from schema import Schema, And, Or, Use, SchemaError

from ..command import Command
from ...utils import load_yaml
from ... import api

_VALIDATE_HELP = """\
Validate the yaml file.
"""


class ValidateCommand(Command):
    """
    Validate the provided yaml file.

    validate
        {image-config : The yaml file with the image configuration}
    """

    help = " ".join(_VALIDATE_HELP.splitlines()).strip()

    schema = Schema(
        {
            "image-config": And(
                str, Use(pathlib.Path), lambda p: p.exists(), Use(load_yaml)
            )
        }
    )

    def handle(self):
        params = self.parse_parameters()
        try:
            api.validate_input(params["image-config"])
        except SchemaError as exc:
            self.line("\n".join(exc.autos))
            return 1
        else:
            self.line("OK!")
