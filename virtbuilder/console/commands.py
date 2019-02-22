import os.path

from cleo import Command as BaseCommand

from .. import api
from ..utils import execute_cmd


def validate_stage(stage):
    """ Raise a ValueError if ``stage`` is not one of ``api.CREATE_STAGES`` """
    if stage and stage not in api.CREATE_STAGES:
        msg = f"'stage' must be one of {api.CREATE_STAGES}, not: {stage}"
        raise ValueError(msg)


class Command(BaseCommand):
    """ Base Command class for our application """

    def get_parameters(self):
        """ Return command parameters """
        params = {
            **{key: self.option(key) for key in self._config.options},
            **{key: self.argument(key) for key in self._config.arguments},
        }
        return params


class CreateCommand(Command):
    """
    Create the VM

    create
        {definition : The yaml file with the image configuration}
        {--stage= : The stage you want to run. Needs to be one of [image,upload,vm]}
        {--no-interactive : The commands will not be displayed before execution}
        {--preview : Preview the commands without executing them}
    """

    def handle(self):
        params = self.get_parameters()
        validate_stage(params["stage"])
        api.validate(params["definition"])
        cmds = api.get_create_commands(
            definition_file=params["definition"], stage=params["stage"]
        )
        for cmd in cmds:
            self.line("\n")
            self.line(cmd)
            self.line("\n")
            if not params["preview"]:
                self.ask("Press Enter to Continue")
                execute_cmd(cmd)


class RemoveCommand(Command):
    """
    Remove the VM

    remove
        {definition : The yaml file with the image configuration}
        {--stage= : The stage you want to run. Needs to be one of [image,upload,vm]}
        {--preview : Preview the commands without executing them}
    """

    def handle(self):
        params = self.get_parameters()
        api.validate(params["definition"])
        cmds = api.get_remove_commands(definition_file=params["definition"])
        for cmd in cmds:
            self.line("\n")
            self.line(cmd)
            self.line("\n")
            if not params["preview"]:
                self.ask("Press Enter to Continue")
                execute_cmd(cmd)


class MultiCommand(Command):
    """
    Execute <c1>command</> on multiple <c1>definitions</>.

    multi
        {command : The action we want to perform. Needs to be one of {"create", "remove}.}
        {definitions* : The definition files for the VMs}
    """

    def handle(self):
        params = self.get_parameters()
        command = params["command"]
        if command not in {"create", "remove"}:
            msg = "command needs to be in {'create', 'remove'}, not: {command}"
            raise ValueError(msg)
        for definition in params["definitions"]:
            self.call(command, definition)


class ValidateCommand(Command):
    """
    Validate the definition file.

    validate
        {definition : The yaml file with the image/VM definition}
    """

    def handle(self):
        params = self.get_parameters()
        api.validate(params["definition"])
        self.line("<c1>OK!</>")
