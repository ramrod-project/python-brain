"""
test CRUD ops

put, list_dir, get, delete

"""
from os import environ
from dict_to_protobuf import protobuf_to_dict
from pytest import fixture, raises
import docker

from .brain import connect, r
from .brain.binary.data import put, get, list_dir, delete
from .brain.queries import RBF
from .brain.brain_pb2 import Binary


CLIENT = docker.from_env()
TEST_FILE_NAME = "TEST_FILE.txt"
TEST_FILE_CONTENT = "content data is binary 灯火 标 and string stuff ".encode('utf-8')

@fixture(scope='module')
def rethink():
    tag = environ.get("TRAVIS_BRANCH", "dev").replace("master", "latest")
    container_name = "brainmoduletestCRUD"
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


def test_ensure_files_table_exists(rethink):
    try:
        r.db("Brain").table_create("Files").run(connect())
    except r.ReqlOpFailedError:
        pass  # table may already exist and that's ok
    RBF.run(connect())  # test it can pull a cursor


def test_put_binary(rethink):
    bin_obj = Binary()
    bin_obj.Name = TEST_FILE_NAME
    bin_obj.Content = TEST_FILE_CONTENT
    obj_dict = protobuf_to_dict(bin_obj)
    put(obj_dict)


def test_obj_in_listing(rethink):
    assert TEST_FILE_NAME in list_dir()


def test_get_file(rethink):
    assert get(TEST_FILE_NAME)['Content'] == TEST_FILE_CONTENT


def test_remove_file(rethink):
    assert TEST_FILE_NAME in list_dir()
    assert delete(TEST_FILE_NAME)
    assert TEST_FILE_NAME not in list_dir()


def test_remove_non_existant_file(rethink):
    assert TEST_FILE_NAME not in list_dir()
    assert delete(TEST_FILE_NAME)


def test_verify_put_command(rethink):
    bin_obj = Binary()
    bin_obj.Name = TEST_FILE_NAME
    bin_obj.Content = TEST_FILE_CONTENT
    obj_dict = protobuf_to_dict(bin_obj)
    put(obj_dict, verify=True)


def test_huge_insert_fails_needs_split(rethink):
    """
    134217727 is the biggest query size
    make an object bigger than that
    add the overhead of the other query params, should be over
    :param rethink:
    :return:
    """
    big_content = ("a"*134217727).encode("utf-8")
    bin_obj = Binary()
    bin_obj.Name = TEST_FILE_NAME
    bin_obj.Content = TEST_FILE_CONTENT
    obj_dict = protobuf_to_dict(bin_obj)
    obj_dict["Content"] = big_content
    with raises(ValueError):
        try:
            put(obj_dict)
        except ValueError as ValErr:
            assert "greater than maximum (134217727)" in str(ValErr)
            raise ValErr
