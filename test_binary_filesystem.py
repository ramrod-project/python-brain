"""
test CRUD ops

put, list_dir, get, delete

"""
from os import environ, remove
from pytest import fixture, raises
import docker
import tempfile
from time import sleep
from multiprocessing import Process
from .brain import connect, r
from .brain.binary.data import put, get, list_dir, delete
from .brain.queries import RBF
from .brain.brain_pb2 import Binary
from .brain.binary import filesystem as bfs
from .test_put_and_get_binary import test_ensure_files_table_exists as check_files_table


CLIENT = docker.from_env()
TEST_FILE_NAME = "TEST_FILE.txt"
TEST_FILE_CONTENT = "content data is binary 灯火 标 and string stuff ".encode('utf-8')

@fixture(scope='module')
def rethink():
    tag = environ.get("TRAVIS_BRANCH", "dev").replace("master", "latest")
    container_name = "brainmoduletestFilesystem"
    CLIENT.containers.run(
        "ramrodpcp/database-brain:{}".format(tag),
        name=container_name,
        detach=True,
        ports={"28015/tcp": 28015},
        remove=True
    )
    check_files_table(None)
    with tempfile.TemporaryDirectory() as tf:
        p = Process(target=bfs.start_filesystem, args=(tf,))
        p.start()
        yield tf
        p.terminate()
        p.join(5)
    # Teardown for module tests
    containers = CLIENT.containers.list()
    for container in containers:
        if container.name == container_name:
            container.stop()
            break


def test_temp_folder_exists(rethink):
    sleep(3) #account for fuse startup
    assert rethink


def test_write_a_file(rethink):
    with open("{}/{}".format(rethink, TEST_FILE_NAME), "wb") as f:
        f.write(TEST_FILE_CONTENT)
    sleep(2) #push to database is async after close
    assert TEST_FILE_NAME in list_dir()


def test_read_a_file(rethink):
    with open("{}/{}".format(rethink, TEST_FILE_NAME), "rb") as f:
        local_file_content = f.read()
    assert TEST_FILE_CONTENT == local_file_content


def test_delete_a_file(rethink):
    """
    default filesystem remove is disabled by default

    can be enabled by setting brain.binary.filesystem.ALLOW_REMOVE to true before launching the fs
    :param rethink:
    :return:
    """
    remove("{}/{}".format(rethink, TEST_FILE_NAME))
    sleep(4)
    assert TEST_FILE_NAME in list_dir()

