__author__ = 'sean-abbott'

import os
import sys 

import click
from jinja2 import Environment, PackageLoader

TEMPLATE_LIST = [
    {'src': 'setup.py.j2', 'dest': 'setup.py'}    
]

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

def _render_template(env, j_ctx_dict, src_file, dest_file):
    template = env.get_template(src_file)
    try:
        with open(dest_file, 'w') as f:
            f.write(template.render(j_ctx_dict))
    except:
        raise

    return True

def _create_skel_files(j_ctx_dict, template_list):
    try:
        jinja_env = Environment(loader=PackageLoader('abe', 'templates'))
    except:
        click.echo("Error loading templates...")
        raise
    for target in TEMPLATE_LIST:
        _render_template(jinja_env, j_ctx_dict)

def _update_template_paths(j_ctx_dict):
    new_list = []
    for template in TEMPLATE_LIST:
        new_list.append( {
            'src': template['src']),
            'dest': os.path.join(j_ctx_dict['target_dir'], template['dest'])
            })

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

    final_template_list = _update_template_paths(jinja_context_dir)

    _create_skel_dirs(jinja_context_dir)
    _create_skel_files(jinja_context_dir, final_template_list)
