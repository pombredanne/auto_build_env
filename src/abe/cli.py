__author__ = 'sean-abbott'

# third party
import click

# this package
import create_skeleton

cli = click.CommandCollection(sources=[
    create_skeleton.cli,
    create_build_env.cli
    ])
