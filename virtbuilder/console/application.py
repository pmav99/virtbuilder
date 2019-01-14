from cleo import Application

from .commands import BuildCommand
from .commands import UploadCommand


def main():
    application = Application()
    application.add(BuildCommand())
    application.add(UploadCommand())
    application.run()
