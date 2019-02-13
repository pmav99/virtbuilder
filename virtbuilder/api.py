import os.path
import pathlib

from pprint import pprint as pp

from .schemas import FullSchema
from .utils import load_yaml, display_cmd, execute_cmd

SINGLE_SEPARATOR = " "
MULTI_SEPARATOR = " \\\n  "


def validate(definition_file):
    """ Raise a SchemaError if the provided data are not not valid """
    data = load_yaml(definition_file)
    FullSchema.validate(data)


def build_image_cmd(data, singleline=False) -> str:
    general = data["general"]
    image = data["image"]
    config = data["image"].pop("config", {})
    provision = config.pop("provision", [])

    parts = [
        f"virt-builder",
        f"{general['os-name']}-{general['os-version']}",
        f"--format {general['format']}",
        f"--output {general['name']}.{general['format']}",
        f"--hostname {general['name']}",
    ]
    # build time options
    for key, value in image.items():
        # no-sync is a boolean flag and not a key-value pair
        if key == "no-sync":
            if value is True:
                parts.append(f"--{key}")
        else:
            if isinstance(value, str):
                value = os.path.expandvars(value)
            parts.append(f'--{key} "{value}"')

    for key, value in config.items():
        # update & selinux-relabel are boolean flags and not key-value pairs
        if key in {"update", "selinux-relabel"}:
            if value is True:
                parts.append(f"--{key}")
        else:
            if isinstance(value, str):
                value = os.path.expandvars(value)
            parts.append(f'--{key} "{value}"')

    for item in provision:
        for key, value in item.items():
            # install & uninstall are comma separated lists
            if key in {"install", "uninstall"}:
                parts.append(f'--{key} "{",".join(value)}"')
            else:
                if isinstance(value, str):
                    value = os.path.expandvars(value)
                parts.append(f'--{key} "{value}"')

    sep = SINGLE_SEPARATOR if singleline else MULTI_SEPARATOR
    cmd = sep.join(parts)
    return cmd


def build_volume_cmd(data, singleline=False):
    general = data["general"]
    image = pathlib.Path(f"{general['name']}.{general['format']}").resolve()
    image_size = image.stat().st_size
    create_volume_parts = [
        f"virsh",
        f"--connect {general['uri']}",
        f"vol-create-as",
        f"--pool {general['pool']}",
        f"--name {general['name']}",
        f"--format {general['format']}",
        f"--capacity {image_size}",
    ]
    sep = SINGLE_SEPARATOR if singleline else MULTI_SEPARATOR
    cmd = sep.join(create_volume_parts)
    return cmd


def build_upload_cmd(data, singleline=False):
    general = data["general"]
    image = pathlib.Path(f"{general['name']}.{general['format']}").resolve()
    upload_image_parts = [
        f"virsh",
        f"--connect {general['uri']}",
        f"vol-upload",
        f"--pool {general['pool']}",
        f"--vol {general['name']}",
        f"--file {image.as_posix()}",
    ]
    sep = SINGLE_SEPARATOR if singleline else MULTI_SEPARATOR
    cmd = sep.join(upload_image_parts)
    return cmd


def build_vm_cmd(data, singleline=False):
    general = data["general"]
    vm = data["vm"]
    parts = [
        f"virt-install",
        f"--connect {general['uri']}",
        f"--import",
        f"--name {general['name']}",
        f"--os-variant {general['os-type']}",
    ]
    for key, value in data["vm"].items():
        parts.append(f"--{key} {value}")
    sep = SINGLE_SEPARATOR if singleline else MULTI_SEPARATOR
    cmd = sep.join(parts)
    return cmd


BUILD_COMMAND_DISPATCHER = {
    "image": build_image_cmd,
    "volume": build_volume_cmd,
    "upload": build_upload_cmd,
    "vm": build_vm_cmd,
}


def build_commands(data, stage):
    if stage:
        func = BUILD_COMMAND_DISPATCHER[stage]
        cmds = [func(data)]
    else:
        cmds = [
            build_image_cmd(data),
            build_volume_cmd(data),
            build_upload_cmd(data),
            build_vm_cmd(data),
        ]
    return cmds


def get_create_commands(definition_file, stage=None):
    data = load_yaml(definition_file)
    cmds = build_commands(data, stage=stage)
    return cmds
