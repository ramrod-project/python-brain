"""
Pytest file for the connection wrapper
"""

from os import environ
from pytest import fixture, raises
import docker

from .brain import connect, r
from .brain.connection import DefaultConnection, BrainNotReady
CLIENT = docker.from_env()


@fixture(scope='module')
def rethink():
    try:
        tag = environ.get("TRAVIS_BRANCH", "dev").replace("master", "latest")
    except KeyError:
        tag = "latest"
    container_name = "brainmoduletest"
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



def test_brain_interface(rethink):
    return connect()

def test_brain_interface_with_host(rethink):
    import rethinkdb
    return connect("localhost", rethinkdb.DEFAULT_PORT)


def test_direct_interface(rethink):
    r.connect()

if __name__ == "__main__":
    a = rethink()
    c = test_brain_interface(a.__next__())
    try:
        a.__next__()
    except StopIteration:
        pass
