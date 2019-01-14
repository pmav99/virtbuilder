import json
import schema

from cleo import Application
from cleo import Command
from jinja2 import Template


class BuildCommand(Command):
    """
    Build the image based on the provided definition

    build
        {definition : The json file with the image definition}
        {--preview=false : Preview the virt-builder command}
    """

    def handle(self):
        print("Yay!")


class UploadCommand(Command):
    """
    Upload an image based on the provided definition

    upload
        {image : The json file with the image definition}
        {pool : The pool where we want to upload}
        {volume : The name of the volume}
        {--u|uri=qemu:///system : The URI of the hypervisor to connect to}

    """


def main():
    application = Application()
    application.add(BuildCommand())
    application.add(UploadCommand())
    application.run()
