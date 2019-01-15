import pathlib

from schema import Schema, And, Or, Use, Optional, SchemaError

from ..command import Command
from ...utils import open_json
from ... import api

_UPLOAD_HELP = """\
Uploads an image to a </c1>libvirt</> pool using <c1>virsh</>.
"""


class UploadCommand(Command):
    """
    Upload an image based on the provided configuration

    upload
        {filename : The json file with the image configuration}
        {volume? : The name of the volume. If it is omitted, defaults to the filename's stem}
        {--pool=default : The pool where we want to upload}
        {--uri=qemu:///system : The URI of the hypervisor to connect to}
        {--format=qcow2 : The format of the image}
    """

    help = " ".join(_UPLOAD_HELP.splitlines()).strip()

    schema = Schema(
        {
            "filename": And(str, len, Use(pathlib.Path), lambda p: p.exists()),
            "volume": Or(None, And(str, len)),
            "pool": And(str, len),
            "format": And(str, len, lambda n: n in {"qcow2", "img"}),
            "uri": And(str, len),
        }
    )

    def handle(self):
        params = self.parse_parameters()
        if params.volume is None:
            params.volume = params.filename.stem

        api.create_volume(
            params.uri, params.pool, params.volume, params.filename, params.format
        )
        api.upload_volume(params.uri, params.pool, params.volume, params.filename)
