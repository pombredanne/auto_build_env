__author__ = 'sean-abbott'

from jinja2 import Environment

def render_template(jinja_env, jinja_ctx, src_file, dest_file):
    template = jinja_env.get_template(src_file)
    try:
        with open(dest_file, 'w') as f:
            f.write(template.render(jinja_ctx))
    except:
        raise
