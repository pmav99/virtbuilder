from cleo import Command as BaseCommand
import schema


class Command(BaseCommand):
    """ Base Command class for our application """

    schema = None

    def get_parameters(self):
        """ Return command parameters """
        params = {
            **{key: self.option(key) for key in self._config.options},
            **{key: self.argument(key) for key in self._config.arguments},
        }
        return params

    def parse_parameters(self, validate=True):
        """ Return the parameters if they validate correctly """
        params = self.get_parameters()
        if validate and isinstance(self.schema, schema.Schema):
            params = self.schema.validate(params)
        return params
