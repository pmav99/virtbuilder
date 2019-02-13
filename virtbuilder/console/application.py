from cleo import Application

from .commands import CreateCommand
from .commands import PreviewCommand
from .commands import ValidateCommand


def main():
    application = Application(complete=False)
    application.add(CreateCommand())
    application.add(PreviewCommand())
    application.add(ValidateCommand())
    application.run()
