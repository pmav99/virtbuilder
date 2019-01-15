import shlex
import subprocess

from . import env


def generate_command_from_template(template, definition):
    template = env.get_template(template)
    out = template.render(d=definition)
    return out


def execute_cmd(cmd):
    cmd = shlex.split(cmd)
    # newlines seem to confuse shlex
    cmd = [elem for elem in cmd if elem != "\n"]
    return subprocess.check_call(cmd)
