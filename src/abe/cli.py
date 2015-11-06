__author__ = 'sean-abbott'

import os
import sys 

import click
from jinja2 import Environment, PackageLoader

def _create_skel_dirs(j_ctx_dict):
    dir_list = [
            'src',
            'test',
            os.path.join('src', os.path.basename(j_ctx_dict['target_dir']))
            ]
    if not os.path.exists(os.path.dirname(j_ctx_dict['target_dir'])):
        click.echo("Parent directory must already exist")
    try:
        os.mkdir(j_ctx_dict['target_dir'])
        for d in dir_list:
            os.mkdir(os.path.join(j_ctx_dict['target_dir'], d))
    except OSError as oe:
        if oe.errno == 2:
            click.echo('Failed to create directory {}'.format(oe.filename))
            sys.exit(1)
        else:
            raise

def _template_in_setup_py(env, j_ctx_dict):
    template = env.get_template('setup.py.j2')
    try:
        with open(os.path.join(j_ctx_dict['target_dir'], 'setup.py'), 'w') as f:
            f.write(template.render(j_ctx_dict))
    except:
        raise

    return True

def _create_skel_files(j_ctx_dict):
    try:
        jinja_env = Environment(loader=PackageLoader('abe', 'templates'))
    except:
        click.echo("Error loading templates...")
        raise

    setup_py_success = _template_in_setup_py(jinja_env, j_ctx_dict)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('project_name')
@click.option('--target_dir')
def create_skeleton(project_name, target_dir=None):
    if target_dir == None:
        target_dir = os.path.join(os.getcwd(), project_name)
    
    if os.path.exists(target_dir):
        click.echo("Target directory exists.  Exiting.")
        sys.exit(1)

    jinja_context_dir = {
            'project_name': project_name,
            'target_dir': target_dir
            }

    _create_skel_dirs(jinja_context_dir)
    _create_skel_files(jinja_context_dir)
