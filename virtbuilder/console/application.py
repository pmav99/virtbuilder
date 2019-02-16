from cleo import Application

from .commands import CreateCommand
from .commands import RemoveCommand
from .commands import ValidateCommand


def main():
    application = Application(complete=False)
    application.add(CreateCommand())
    application.add(RemoveCommand())
    application.add(ValidateCommand())
    application.run()
