"""
Pytest file should error if the database is not a brain
"""

from os import environ
from pytest import fixture, raises
import docker
from time import sleep
from .brain import connect
from .brain.connection import DefaultConnection, BrainNotReady
CLIENT = docker.from_env()



@fixture(scope='module')
def default_rethink():
    container_name = "brainmoduledefaulttest"
    CLIENT.containers.run(
        "rethinkdb:2.3.6",
        name=container_name,
        detach=True,
        ports={"28015/tcp": 28015},
        remove=True
    )
    sleep(5)
    yield True
    # Teardown for module tests
    containers = CLIENT.containers.list()
    for container in containers:
        if container.name == container_name:
            container.stop()
            break

def test_not_brain_interface(default_rethink):
    with raises(BrainNotReady):
        connect()
