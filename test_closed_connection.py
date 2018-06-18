"""
Pytest file for the connection wrapper
"""

from os import environ
from pytest import fixture, raises
import docker

from .brain import connect
from .brain.queries import plugin_exists, create_plugin, destroy_plugin, RPX
from .brain.connection import DefaultConnection, BrainNotReady
from rethinkdb.errors import ReqlDriverError


CLIENT = docker.from_env()
CONTAINER_NAME = "brainmoduletest_closed_connection"
PLUGIN_NAME = "test_plugin_closed_conn"


@fixture(scope='module')
def rethink():
    tag = environ.get("TRAVIS_BRANCH", "dev").replace("master", "latest")
    container_name = CONTAINER_NAME
    CLIENT.containers.run(
        "ramrodpcp/database-brain:{}".format(tag),
        name=container_name,
        detach=True,
        ports={"28015/tcp": 28015},
        remove=True
    )
    yield True
    # Teardown for module tests
    containers = CLIENT.containers.list()
    for container in containers:
        if container.name == container_name:
            container.stop()
            break


def test_default_dumb_close(rethink):
    c = connect()
    RPX.table_create(PLUGIN_NAME).run(c)
    c.close()
    with raises(ReqlDriverError):
        RPX.table(PLUGIN_NAME).run(c)
    assert destroy_plugin(PLUGIN_NAME, c) #this should reconnect


def test_dumb_close(rethink):
    c = connect()
    assert create_plugin(PLUGIN_NAME, c)
    assert plugin_exists(PLUGIN_NAME, c)
    c.close() #oopsie daisy
    assert plugin_exists(PLUGIN_NAME, c) #this should auto-reconnect
    assert destroy_plugin(PLUGIN_NAME, c) #this shouldn't need to



def test_malicious_close(rethink):
    c = connect()
    assert create_plugin(PLUGIN_NAME, c)
    assert plugin_exists(PLUGIN_NAME, c)
    containers = CLIENT.containers.list()
    for container in containers:
        if container.name == CONTAINER_NAME:
            container.stop()
            break
    with raises(ValueError): #caught by the rethinkerror
        plugin_exists(PLUGIN_NAME, c)  # this should auto-reconnect

