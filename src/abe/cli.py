__author__ = 'sean-abbott'

import os
import sys 
import shutil
import inspect
from pkg_resources import resource_filename

import click
from jinja2 import Environment, PackageLoader

TEMPLATE_LIST = [
        {'src': 'setup.py.j2', 'target_filename': 'setup.py', 'target_path': ''}    
]
DUMMY_DIR_LIST = [
        'dependencies'
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

def _copy_dummy_dirs(j_ctx_dict):
    for d in DUMMY_DIR_LIST:
        shutil.copytree(
                os.path.join(j_ctx_dict['files_dir'], d),
                os.path.join(j_ctx_dict['target_dir'], d)
                )

def _create_skel_files(j_ctx_dict, template_list):
    try:
        jinja_env = Environment(loader=PackageLoader('abe', 'templates'))
    except:
        click.echo("Error loading templates...")
        raise
    for target in template_list:
        _render_template(
                jinja_env,
                j_ctx_dict,
                target['src'],
                target['target_path']
                )

def _update_template_paths(j_ctx_dict):
    new_list = []
    for template in TEMPLATE_LIST:
        new_list.append({
            'src': template['src'],
            'target_filename': template['target_filename'],
            'target_path': os.path.join(
                    j_ctx_dict['target_dir'],
                    template['target_path'],
                    template['target_filename']
                    )
            })

    return new_list

def _get_files_dir():
    # http://peak.telecommunity.com/DevCenter/PkgResources#resource-extraction
    pdir = resource_filename(__name__, 'files')
    if pdir is not None:
        return pdir
    else:
        click.echo("Error retreiving necessary file")
        sys.exit(1)

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

    jinja_context_dict = {
            'project_name': project_name,
            'target_dir': target_dir,
            'files_dir': _get_files_dir()
            }

    final_template_list = _update_template_paths(jinja_context_dict)

    _create_skel_dirs(jinja_context_dict)
    _create_skel_files(jinja_context_dict, final_template_list)
    _copy_dummy_dirs(jinja_context_dict)
