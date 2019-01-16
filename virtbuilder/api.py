import shlex
import subprocess

from .schemas import virt_builder_schema
from . import env


def validate_input(input_yaml):
    virt_builder_schema.validate(input_yaml)
    pass


def generate_command_from_template(template, definition):
    template = env.get_template(template)
    out = template.render(d=definition)
    return out


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
