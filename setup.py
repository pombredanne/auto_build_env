__author__ = 'sean-abbott'

from setuptools import setup
from distutils.cmd import Command
import versioneer

def readme():
    with open('README.rst') as f:
        return f.read()

def BaseCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

def RunDepCommand(BaseCommand):

    description = "install runtime dependencies"
    def run(self):
        cmd = ["pip", "install", "-r", "requirements.txt"]
        ret = subprocess.call(cmd)
        sys.exit(ret)

def get_command_class():
    base = versioneer.get_cmdclass()
    base['install_run_deps'] = RunDepCommand
    return base

setup(
  name='auto_build_env',
  version=versioneer.get_version(),
  cmdclass=get_command_class(),
  description='Automatic Build Environment Generator',
  long_description=readme(),
  author='Sean Abbott',
  author_email='sean.abbott@datarobot.com',
  package_dir={'': 'src'},
  packages=['abe'],
  package_data={
    '': ['*.rst']
  },
  entry_points={
    'console_scripts': ['abe=abe.cli:main']
  },
)
