import time

import click

from launchkey.factories import ServiceFactory, DirectoryFactory

SUCCESS_COLOR = "green"
FAILURE_COLOR = "red"


def print_result(message, data={}, color=None):
    for item in data.items():
        message += "\n\t%s:\t%s" % item
    click.secho(message, fg=color)


def get_service_client(service_id, factory):
    if isinstance(factory, ServiceFactory):
        return factory.make_service_client()
    else:
        return factory.make_service_client(service_id)


def get_directory_client(directory_id, factory):
    if isinstance(factory, ServiceFactory):
        raise TypeError("Services cannot issue directory commands. "
                        "Please use either a Directory or Organization "
                        "for your entity_id, entity_type, and private_key.")
    elif isinstance(factory, DirectoryFactory):
        return factory.make_directory_client()
    else:
        return factory.make_directory_client(directory_id)


def wait_for_response(func, args=[], kwargs={}):
    response = None
    while not response:
        time.sleep(0.5)
        click.echo(".", nl=False)
        response = func(*args, **kwargs)
    click.echo("\n")
    return response
