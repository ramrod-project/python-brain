from pytest import raises
import docker

from .brain import connect, r
from .brain.connection import DefaultConnection, BrainNotReady
CLIENT = docker.from_env()


def test_database_not_up():
    with raises (BrainNotReady):
        connect()

def test_legacy_connect_error():
    from rethinkdb.errors import ReqlDriverError
    with raises(ReqlDriverError):
        r.connect()