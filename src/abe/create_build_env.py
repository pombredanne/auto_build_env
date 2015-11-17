__author__ = 'sean-abbott'

# batteries included
import os
from pkg_resources import resource_filename
import shutil
import copy
import glob
import json

# third party
import click
from jinja2 import Environment, PackageLoader
from pykwalify.core import Core
import pykwalify
import yaml
import docker

# this module
from errors import AbeConfigError
import utils

# YELLOW create_skeleton uses a similar pattern.  abstract
BUILDENV_TEMPLATE_LIST = [
    {'src': 'Dockerfile.j2', 'target_filename': 'Dockerfile', 'target_path': ''}
]

DEP_COPY_KEYLIST = ['build_dependency_file']

PACKAGE_COMMANDS = {
    'deb': {'package_family': {
                'updatecmd': 'apt-get update',
                'installcmd': 'apt-get -y --no-install-recommends install',
                'python_pkg_pkg': 'python-pip'
                }
            }
}

def _validate_osdep_schema(source_filename, schema_filename):
    # pykwalify import is awkward
    #import pdb; pdb.set_trace()
    c = Core(source_file=source_filename, schema_files=[schema_filename])
    c.validate(raise_exception=True)

def _get_os_dependencies(options_dict):
    if not os.path.isfile(options_dict['os_dependency_file']):
        raise AbeConfigError("Can't find dependency file. Exiting")

    with open(options_dict['os_dependency_file'], 'r') as yf:
        raw_deps_dict = yaml.load(yf.read())
    
    if 'schema_version' not in raw_deps_dict:
        raise AbeConfigError("Schema version unspecified in {}. Exiting".format(
            options_dict['os_dependency_file']
            ))
        
    schema_name = "os_dependencies.schema.{}.yml".format(
            raw_deps_dict['schema_version']
            )
    schema_filename = resource_filename(__name__, "schema/{}".format(
        schema_name
        ))
    try:
        _validate_osdep_schema(
                options_dict['os_dependency_file'],
                schema_filename
                )
    except pykwalify.errors.SchemaError as se:
        click.echo("Schema validation error.")
        click.echo("Please run pykwalify before submitting os_dependencies changes")
        raise se

    deps_dict = _process_deps_dict(raw_deps_dict, options_dict)

    return deps_dict

# YELLOW:  We should somewhere/somehow validate that we have code for each
# dependency in the schema enumeration for package_family
def _explode_os_package_commands(dep_dict, options):
    """ for each member of dep_list, add appropriate keys for creating
        the Dockerfile

        This function modifies the dictionary in place (pass-by-reference)
    """
    for env in dep_dict['dep_list']:
        env.update(PACKAGE_COMMANDS[env['package_family']])
        env['build_dependency_file'] = os.path.join(
                'dependencies',
                os.path.basename(options['build_dependency_file'])
                )

def _process_deps_dict(dep_dict, options):
    """ runs a series of calculations to modify the dictionary, adding or
        changing values
    """
    new_dep_dict = copy.deepcopy(dep_dict)
    _explode_os_package_commands(new_dep_dict, options)
    return new_dep_dict

def _template_in_buildenv_files(dirpath, env_dict, jinja_env):
    """ create Dockerfile and any necessary scripts """
    for t in BUILDENV_TEMPLATE_LIST:
        dest = os.path.join(dirpath, t['target_path'], t['target_filename'])
        utils.render_template(jinja_env, env_dict, t['src'], dest)

def _copy_dependency_files(dirpath, options):
    """ copy the python dependency files into the builddir/dependencies """
    dep_path = os.path.join(dirpath, 'dependencies')
    try:
        os.makedirs(dep_path)
    except OSError as oe:
        # YELLOW best if we parse this a little
        click.echo("{} may already exist".format(dep_path))
    
    for key in DEP_COPY_KEYLIST:
        shutil.copy(options[key], dep_path)

def _create_dabbmd(osenv, component_name, buildenv_path):
    # RED this needs to be set at the abe level and passed in
    with open('.abe_config.yml', 'r') as f:
        abe_config_dict = yaml.load(f)

    # YELLOW we're probably goingto want this to be more fine-grained
    dabbmd_dict = {}
    dabbmd_dict.update(abe_config_dict)

    dabbmd_dict['component_name'] = component_name

    # RED yeah, this is needs to have a known way of getting the right version
    dabbmd_dict['buildenv_version'] = 'latest'

    with open(os.path.join(buildenv_path, 'dabbmd.json'), 'w') as f:
        json.dump(dabbmd_dict, f)

def _get_component_name():
    """ get the component name from setup.py """
    # RED what I actually want is to get the name from the correct place
    # i.e., setup.py, pom.xml, package.json, etc.
    return os.path.basename(os.getcwd())

def _create_build_directories(osenv_list, options_dict):
    wd = options_dict['working_dir']
    component_name = _get_component_name()

    try:
        jinja_env = Environment(loader=PackageLoader('abe', 'templates'))
    except:
        click.echo("Error loading templates...")
        raise

    for osenv in osenv_list:
        buildenv_dirname = "buildenv_{}-{}".format(
                osenv['os_name'],
                osenv['os_version_id']
                )
        buildenv_path = os.path.join(wd, buildenv_dirname)
        try:
            os.makedirs(buildenv_path)
        except OSError as oe:
            # YELLOW best if we parse this a little
            click.echo("{} may already exist".format(buildenv_path))

        _template_in_buildenv_files(buildenv_path, osenv, jinja_env)
        _copy_dependency_files(buildenv_path, options_dict)
        _create_dabbmd(osenv, component_name, buildenv_path)

def _get_docker_tag(docker_dir):
    """ get the dabbmd.json file and return the tag string from it """
    with open(os.path.join(docker_dir, 'dabbmd.json'), 'r') as f:
        dabbmd_dict = json.load(f)

    docker_tag = "{}/{}/{}:{}".format(
            dabbmd_dict['docker_repository'], 
            dabbmd_dict['docker_username'],
            dabbmd_dict['component_name'],
            dabbmd_dict['buildenv_version']
            )
    return docker_tag
    

def run_buildenv_builds(work_dir):
    """ change to each buildenv directory in working_dir and run the builds """
    c = docker.Client(base_url='unix://var/run/docker.sock', version='auto')
    for d in glob.glob(os.path.join(work_dir, 'buildenv*')):
        # RED this is way to fast and dirty, even for this project
        for line in c.build(path=d, tag=_get_docker_tag(d)):
            click.echo(line)

@click.group()
def cli():
    pass

@cli.command()
@click.option(
        '--working-dir',
        help="The directory to place the Dockerfile"
        )
@click.option(
        '--os-dependency-file',
        help="path to the os_depedency.yml file you're using",
        show_default=True,
        default=os.path.join('dependencies', 'os_dependencies.yml')
        )
@click.option(
        '--build_dependency_file',
        help="path to the language build dependencies",
        show_default=True,
        default=os.path.join('dependencies', 'build_requirements.txt')
        )
def create_build_env(**kwargs):
    if kwargs.get('working_dir', None) is None:
        kwargs['working_dir'] = os.path.join(os.getcwd(), 'work')

    dependency_dict = _get_os_dependencies(kwargs)

    _create_build_directories(dependency_dict['dep_list'], kwargs)
    run_buildenv_builds(kwargs['working_dir'])
