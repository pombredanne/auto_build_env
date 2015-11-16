__author__ = 'sean-abbott'

# batteries included
import os

# third party
import click
from jinja2 import Environment, PackageLoader
from pykwalify.core import Core

def _get_os_depedencies(options_dict):
    if not os.path.isfile(options_dict['dependency_file']):
        click.echo("Can't find dependency file. Exiting")
        sys.exit(1)

    

@click.group()
def cli():
    pass

@cli.command()
@click.option(
        '--working-dir',
        help="The directory to place the Dockerfile"
        )
@click.option(
        '--dependency-file',
        help="path to the os_depedency.yml file you're using",
        show_default=True,
        default=os.path.join('dependencies', 'os_dependencies.yml')
        )
def create_build_env(**kwargs):
    if kwargs['working_dir'] is None:
        working_dir = os.path.join(os.getcwd(), 'work')

    depedency_dict = _get_os_dependencies(kwargs)

    _create_build_directory()
