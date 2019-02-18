import os.path
import pathlib

from pprint import pprint as pp

from .schemas import FullSchema
from .utils import load_yaml, execute_cmd

SINGLE_SEPARATOR = " "
MULTI_SEPARATOR = " \\\n  "


def validate(definition_file):
    """ Raise a SchemaError if the provided data are not not valid """
    data = load_yaml(definition_file)
    FullSchema.validate(data)


def create_image_cmd(data, singleline=False) -> str:
    general = data["general"]
    image = data["image"]
    config = data["image"].pop("config", {})
    provision = config.pop("provision", [])

    parts = [
        f"virt-builder",
        f"{general['os-name']}-{general['os-version']}",
        f"--verbose" if general.get("verbose") else "",
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
    cmd = sep.join((p for p in parts if p))
    return cmd


def create_volume_cmd(data, singleline=False):
    general = data["general"]
    image = pathlib.Path(f"{general['name']}.{general['format']}").resolve()
    image_size = data["image"]["size"]
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


def create_upload_cmd(data, singleline=False):
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


def create_cleanup_cmd(data, singleline=False):
    general = data["general"]
    parts = [f"/usr/bin/rm", f"{data['general']['name']}.{data['general']['format']}"]
    sep = SINGLE_SEPARATOR if singleline else MULTI_SEPARATOR
    cmd = sep.join(parts)
    return cmd


def create_vm_cmd(data, singleline=False):
    general = data["general"]
    vm = data["vm"]
    os_variant = general.get("os-variant", general["os-name"] + general["os-version"])
    parts = [
        f"virt-install",
        f"--connect {general['uri']}",
        f"--import",
        f"--name {general['name']}",
        f"--os-variant {os_variant}",
    ]
    for key, value in data["vm"].items():
        parts.append(f"--{key} {value}")
    sep = SINGLE_SEPARATOR if singleline else MULTI_SEPARATOR
    cmd = sep.join(parts)
    return cmd


def _get_create_commands(data, stage):
    if stage:
        func = CREATE_COMMAND_DISPATCHER[stage]
        cmds = [func(data)]
    else:
        cmds = [
            create_image_cmd(data),
            create_volume_cmd(data),
            create_upload_cmd(data),
            create_cleanup_cmd(data, singleline=True),
            create_vm_cmd(data),
        ]
    return cmds


def get_create_commands(definition_file, stage=None):
    data = load_yaml(definition_file)
    cmds = _get_create_commands(data, stage=stage)
    return cmds


def get_remove_commands(definition_file):
    data = load_yaml(definition_file)
    name = data["general"]["name"]
    uri = data["general"]["uri"]
    cmds = [
        f"virsh --connect {uri} destroy {name}",
        f"virsh --connect {uri} undefine --remove-all-storage {name}",
    ]
    return cmds


CREATE_COMMAND_DISPATCHER = {
    "image": create_image_cmd,
    "volume": create_volume_cmd,
    "upload": create_upload_cmd,
    "cleanup": create_cleanup_cmd,
    "vm": create_vm_cmd,
}


CREATE_STAGES = list(CREATE_COMMAND_DISPATCHER.keys())
