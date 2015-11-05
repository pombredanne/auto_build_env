__author__ = 'sean-abbott'

from setuptools import setup, Command
import versioneer

versioneer.VCS = 'git'
versioneer.versionfile_source = 'src/auto_build_env/_version.py'
versioneer.versionfile_build = 'auto_build_env/_version.py'
versioneer.tag_prefix = ''  # tags are like 1.2.0
versioneer.parentdir_prefix = 'auto-build_env-'  # dirname like 'tool-1.2.0'


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

    cmd = ["pip", "install", "-r", "requirements.txt"]
    ret = subprocess.call(cmd)
    sys.exit(ret)

setup(
  name='auto_build_env',
  version=versioneer.get_version(),
  cmdclass=versioneer.get_cmdclass(),
  description='Automatic Build Environment Generator',
  long_descritpion=readme(),
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
  cmdclass['install_run_depedencies'] = RunDepCommand
)
