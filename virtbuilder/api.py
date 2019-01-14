import shlex
import subprocess

from . import env


def generate_virt_builder_command(definition):
    template = env.get_template("virt_builder.j2")
    out = template.render(d=definition)
    return out


def execute_cmd(cmd):
    cmd = shlex.split(cmd)
    # newlines seem to confuse shlex
    cmd = [elem for elem in cmd if elem != "\n"]
    return subprocess.check_call(cmd)
