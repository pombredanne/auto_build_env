__author__ = 'sean-abbott'

# batteries included
import os

# third party
from jinja2 import Environment

def render_template(jinja_env, jinja_ctx, src_file, dest_file):
    """
    Render a jinja template

    :param jinja_env: a jinja2.Environment object
    :param jinja_ctx:  the dictionary providing rendering context
    :param src_file: the source template
    :param dest_file: the destination path
    """
    template = jinja_env.get_template(src_file)
    try:
        with open(dest_file, 'w') as f:
            f.write(template.render(jinja_ctx))
    except:
        raise

def get_option(opt_name, kwargs, config, default=None):
  """ 
  Returns the resolved value of an option. Resolution order is: cmd line args -> config -> default
  :param opt_name: Name of the option to resolve
  :param kwargs: command args
  :param config: dictionary of values read from file
  :param default: default value
  :return: Resolved value
  """                                                                                               
  arg_value = kwargs.get(opt_name, None)
  config_value = config.get(opt_name, None)
  env_value = os.getenv(opt_name.upper(), None) 

  for val in (arg_value, env_value, config_value, default):
    if val is not None:
      return val
  raise ValueError('You must either set {} or provide {} via command line.'.format(opt_name, opt_short_name))
