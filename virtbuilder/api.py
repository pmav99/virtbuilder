import shlex
import subprocess

from .schemas import full_schema
from .utils import execute_cmd


def _generate_build_command_parts(data):
    build = data["build"]
    config = data["build"]["config"]
    parts = [f"virt-builder {build['os']}-{build['version']}"]

    # build time options
    for key, value in build.items():
        if key in {"os", "version", "config"}:
            continue
        # no-sync is a boolean flag and not a key-value pair
        if key == "no-sync":
            if value is True:
                parts.append(f"--{key}")
        else:
            parts.append(f'--{key} "{value}"')

    for key, value in config.items():
        if key == "provision":
            continue
        # update & selinux-relabel are boolean flags and not key-value pairs
        elif key in {"update", "selinux-relabel"}:
            if value is True:
                parts.append(f"--{key}")
        else:
            parts.append(f'--{key} "{value}"')

    if "provision" in config:
        for item in config["provision"]:
            for key, value in item.items():
                # install & uninstall are comma separated lists
                if key in {"install", "uninstall"}:
                    parts.append(f'--{key} "{",".join(value)}"')
                else:
                    parts.append(f'--{key} "{value}"')
    return parts


def generate_build_command(data, singleline=False):
    parts = _generate_build_command_parts(data)
    if singleline:
        cmd = " ".join(parts)
    else:
        cmd = " \\\n           ".join(parts)
    return cmd


def execute_cmd(cmd):
    cmd = shlex.split(cmd)
    # newlines seem to confuse shlex
    cmd = [elem for elem in cmd if elem != "\n"]
    return subprocess.check_call(cmd)


def get_path_size(path):
    return path.stat().st_size


def create_volume(uri, pool, volume_name, filename, fmt):
    image_size = filename.stat().st_size
    cmd = f"virsh --connect {uri} vol-create-as --pool {pool} --name {volume_name} --capacity {image_size} --format {fmt}"
    print(cmd)
    return execute_cmd(cmd)


def upload_volume(uri, pool, volume_name, filename):
    cmd = f"virsh --connect {uri} vol-upload --vol {volume_name} --file {filename} --pool {pool}"
    print(cmd)
    return execute_cmd(cmd)


def create_from_volume(uri, pool, volume):
    pass
    # vol - An existing libvirt storage volume to use. This is specified as ’poolname/volname’.
