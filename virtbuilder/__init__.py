from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(
    loader=PackageLoader("virtbuilder", "templates"),
    # autoescape=select_autoescape(['html', 'xml', 'j2'])
)

__version__ = "0.1.0"
