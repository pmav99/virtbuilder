import pathlib

from schema import Schema, And, Or, Use, SchemaError

from ..command import Command
from ...schemas import definition_schema
from ...utils import load_yaml
from ... import api

_VALIDATE_HELP = """\
Validate the yaml file.
"""


class ValidateCommand(Command):
    """
    Validate the provided yaml file.

    validate
        {definition : The yaml file with the image configuration}
    """

    help = " ".join(_VALIDATE_HELP.splitlines()).strip()

    schema = Schema(
        {
            "definition": And(
                str, Use(pathlib.Path), lambda p: p.exists(), Use(load_yaml)
            )
        }
    )

    def handle(self):
        params = self.parse_parameters()
        definition_schema.validate(params["definition"])
        self.line("OK!")
