"""
Pytest file for the queries
"""

from os import environ
from pytest import fixture, raises
from time import sleep
import docker
from types import GeneratorType
from .brain import connect, r
from .brain.connection import DefaultConnection, BrainNotReady
from .brain import queries
CLIENT = docker.from_env()


TEST_TARGET = {"PluginName":"TestPlugin",
               "Location": "0.0.0.0",
               "Port": "0",
               "Optional": "example"}
TEST_CAPABILITY = [
    {
        "CommandName": "echo",
        "Tooltip": "",
        "Output": True,
        "Inputs": [
                {"Name": "EchoString",
                 "Type": "textbox",
                 "Tooltip": "This string will be echoed back",
                 "Value": ""
                 },
                ],
        "OptionalInputs": []
    },
]

TEST_JOB = {
    "JobTarget": TEST_TARGET,
    "Status": "Ready",
    "StartTime": 7,
    "JobCommand": TEST_CAPABILITY[0]
}

TEST_JOB_EARLY = {
    "JobTarget": TEST_TARGET,
    "Status": "Ready",
    "StartTime": 0,
    "JobCommand": TEST_CAPABILITY[0]
}

TEST_PLUGIN_DATA = {
    "Name": "Harness",
    "State": "Available",
    "DesiredState": "",
    "Interface": "",
    "ExternalPorts": ["5000"],
    "InternalPorts": ["5000"]
}

TEST_PORT_DATA = {
    "InterfaceName": "eth0",
    "Address": "192.168.1.1",
    "TCPPorts": ["5000"],
    "UDPPorts": []
}

TEST_PORT_DATA2 = {
    "InterfaceName": "eth0",
    "Address": "192.168.1.1",
    "TCPPorts": ["6000", "7000"],
    "UDPPorts": ["8000"]
}

@fixture(scope='module')
def rethink():
    sleep(3) #prior test docker needs to shut down
    try:
        tag = environ.get("TRAVIS_BRANCH", "dev").replace("master", "latest")
    except KeyError:
        tag = "latest"
    container_name = "brainmodule_query_test"
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

def is_the_same_job_as(id_job, ref_job):
    if len(ref_job) == 0:
        return False
    same = True
    for entry in ref_job:
        if entry not in id_job:
            same = False
            break
    return same

def test_get_targets_empty_noconn(rethink):
    g = queries.get_targets()
    assert isinstance(g, GeneratorType)
    with raises(StopIteration):
        g.__next__()

def test_get_targets_empty_with_conn(rethink):
    c = connect()
    g = queries.get_targets(c)
    assert isinstance(g, GeneratorType)
    with raises(StopIteration):
        g.__next__()

def test_add_target(rethink):
    inserted = queries.insert_new_target(TEST_TARGET['PluginName'],
                                         TEST_TARGET['Location'],
                                         TEST_TARGET['Port'],
                                         TEST_TARGET['Optional'],
                                         verify_target=False
                                         )
    assert isinstance(inserted, dict)
    assert isinstance(inserted['generated_keys'], list)
    assert len( inserted['generated_keys'] ) == 1

def test_get_targets_one(rethink):
    g = queries.get_targets()
    assert isinstance(g, GeneratorType)
    target = g.__next__()
    assert isinstance(target, dict)
    with raises(StopIteration):
        g.__next__()

def test_get_targets_one_by_plugin(rethink):
    g = queries.get_targets_by_plugin(TEST_TARGET['PluginName'])
    assert isinstance(g, GeneratorType)
    target = g.__next__()
    assert isinstance(target, dict)
    assert TEST_TARGET["Location"] == target['Location']
    assert "id" in target
    with raises(StopIteration):
        g.__next__()

def test_plugin_does_not_exist(rethink):
    g = queries.get_plugin_commands(TEST_TARGET['PluginName'])
    assert isinstance(g, GeneratorType)
    with raises(ValueError):
        g.__next__()

def test_add_plugin(rethink):
    result = queries.create_plugin(TEST_TARGET['PluginName'])
    assert result

def test_verify_plugin_exists(rethink):
    result = queries.plugin_exists(TEST_TARGET['PluginName'])
    assert result

def test_add_bad_plugin(rethink):
    with raises(ValueError):
        queries.create_plugin("ThisIs.Not_Acceptable!>&$")

def test_invalid_plugin_does_not_exist(rethink):
    result = queries.plugin_exists("THISDOESNOTEXIST")
    assert not result

def test_no_plugin_capabilities(rethink):
    g = queries.get_plugin_commands(TEST_TARGET['PluginName'])
    assert isinstance(g, GeneratorType)
    cmds = [x for x in g]
    assert len(cmds) == 0

def test_add_capability(rethink):
    res = queries.advertise_plugin_commands(TEST_TARGET['PluginName'],
                                            TEST_CAPABILITY)


def test_add_command_to_invalid_plugin(rethink):
    with raises(ValueError):
        res = queries.advertise_plugin_commands("INVALIDPLUGIN",
                                                TEST_CAPABILITY)

def test_get_capability(rethink):
    g = queries.get_plugin_commands(TEST_TARGET['PluginName'])
    assert isinstance(g, GeneratorType)
    cmds = [x for x in g]
    assert len(cmds) == 1
    assert cmds[0]["CommandName"] == TEST_CAPABILITY[0]['CommandName']

def test_get_capability_2(rethink):
    res = queries.get_plugin_command(TEST_TARGET['PluginName'],
                                     TEST_CAPABILITY[0]['CommandName'])
    assert isinstance(res, dict)
    assert res["CommandName"] == TEST_CAPABILITY[0]['CommandName']

def test_no_jobs(rethink):
    g = queries.get_jobs(TEST_TARGET['PluginName'])
    assert isinstance(g, GeneratorType)
    with raises(StopIteration):
        g.__next__()

def test_new_job(rethink):
    res = queries.insert_jobs([TEST_JOB])
    assert isinstance(res, dict)
    assert isinstance(res['generated_keys'], list)
    assert len(res['generated_keys']) == 1

def test_found_job(rethink):
    g = queries.get_jobs(TEST_TARGET['PluginName'])
    assert isinstance(g, GeneratorType)
    job = g.__next__()
    del (job['id'])
    assert job == TEST_JOB
    with raises(StopIteration):
        g.__next__()

def test_no_job_for_invalid(rethink):
    g = queries.get_jobs("INVALIDPLUGIN")
    assert isinstance(g, GeneratorType)
    with raises(StopIteration):
        g.__next__()

def test_make_output(rethink):
    g = queries.get_jobs(TEST_TARGET['PluginName'])
    assert isinstance(g, GeneratorType)
    job = g.__next__()
    queries.RBO.insert({"OutputJob":job,
                        "Content": "A"*1027}).run(connect())
    with raises(StopIteration):
        g.__next__()

def test_set_job_done(rethink):
    g = queries.get_jobs(TEST_TARGET['PluginName'])
    assert isinstance(g, GeneratorType)
    job = g.__next__()
    queries.RBJ.get(job['id']).update({"Status": "Done"}).run(connect())
    assert queries.is_job_done(job['id'])
    with raises(StopIteration):
        g.__next__()

def test_is_job_done_bad_id(rethink):
    assert not queries.is_job_done("notarealid")

def test_verify_output_content(rethink):
    job = queries.RBJ.run(connect()).next()
    o = queries.get_output_content(job['id'])
    assert "[truncated]" in o
    oo = queries.get_output_content(job['id'], max_size=1028)
    assert "[truncated]" not in oo

def test_destroy_plugin(rethink):
    assert TEST_TARGET['PluginName'] in list(queries.RPX.table_list().run(connect()))
    assert queries.destroy_plugin(TEST_TARGET['PluginName'])
    assert TEST_TARGET['PluginName'] not in list(queries.RPX.table_list().run(connect()))

def test_create_plugin_controller(rethink):
    res = queries.create_plugin_controller(TEST_PLUGIN_DATA)
    assert isinstance(res, dict)
    assert isinstance(res['generated_keys'], list)
    assert len(res['generated_keys']) == 1

def test_get_plugin_by_name_controller(rethink):
    c = queries.get_plugin_by_name_controller(TEST_PLUGIN_DATA["Name"])
    assert isinstance(c, r.net.DefaultCursor)
    plugin = c.next()
    del plugin["id"]
    assert plugin == TEST_PLUGIN_DATA

def test_create_port_controller(rethink):
    res = queries.create_port_controller(TEST_PORT_DATA)
    assert isinstance(res, dict)
    assert isinstance(res['generated_keys'], list)
    assert len(res['generated_keys']) == 1

def test_get_ports_by_ip_controller(rethink):
    c = queries.get_ports_by_ip_controller(TEST_PORT_DATA["Address"])
    assert isinstance(c, r.net.DefaultCursor)
    port_entry = c.next()
    del port_entry["id"]
    assert port_entry == TEST_PORT_DATA

def test_create_update_port_controller(rethink):
    res = queries.create_port_controller(TEST_PORT_DATA2)
    print(res)
    assert isinstance(res, dict)
    assert res['replaced'] == 1

def test_check_port_conflict(rethink):
    res = queries.create_port_controller(TEST_PORT_DATA)
    assert isinstance(res, dict)
    assert res["errors"] == 1

def test_update_plugin_controller(rethink):
    new_plugin_data = TEST_PLUGIN_DATA
    new_plugin_data["State"] = "Restarting"
    new_plugin_data["DesiredState"] = "Restart"
    res = queries.update_plugin_controller(new_plugin_data)
    assert isinstance(res, dict)
    assert res["replaced"] == 1

def test_get_next_one_job(rethink):
    res = queries.insert_jobs([TEST_JOB])
    assert isinstance(res, dict)
    res = queries.get_next_job(TEST_TARGET['PluginName'])
    assert isinstance(res, dict)
    assert res['StartTime'] == TEST_JOB['StartTime']

def test_insert_early_job(rethink):
    res = queries.insert_jobs([TEST_JOB_EARLY])
    assert isinstance(res, dict)
    res = queries.get_next_job(TEST_TARGET['PluginName'])
    assert isinstance(res, dict)
    assert res['StartTime'] == TEST_JOB_EARLY['StartTime']

def test_confirm_yields_correct_order(rethink):
    res = queries.get_jobs(TEST_TARGET['PluginName'])
    res1 = next(res)
    assert res1['StartTime'] == TEST_JOB_EARLY['StartTime'] #inserted 2nd with earlier start time
    res2 = next(res)
    assert res2['StartTime'] == TEST_JOB['StartTime']
    with raises(StopIteration):
        next(res)


def test_get_next_one_job_none_available(rethink):
    res = queries.get_next_job("INVALIDPLUGIN")
    assert not res

def test_next_job_already_status_done(rethink):
    g = queries.get_jobs(TEST_TARGET['PluginName'])
    for job in g:
        queries.RBJ.get(job['id']).update({"Status": "Done"}).run(connect())
    res = queries.get_next_job(TEST_TARGET['PluginName'])
    assert not res


def test_get_job_by_id(rethink):
    response = queries.insert_jobs([TEST_JOB])
    job_id = response["generated_keys"][0]
    job = queries.get_job_by_id(job_id, connect())
    assert is_the_same_job_as(job, TEST_JOB)

def test_get_job_status(rethink):
    response = queries.insert_jobs([TEST_JOB])
    job_id = response["generated_keys"][0]
    assert queries.get_job_status(job_id, connect()) == "Ready"

def test_update_job_status(rethink):
    response = queries.insert_jobs([TEST_JOB])
    job_id = response["generated_keys"][0]
    queries.update_job_status(job_id, "Done", connect())
    assert queries.is_job_done(job_id, connect())

def test_write_output(rethink):
    response = queries.insert_jobs([TEST_JOB])
    job_id = response["generated_keys"][0]
    content = "Test Output"
    queries.write_output(job_id, content, connect())
    output = queries.get_output_content(job_id, conn=connect())
    assert output == content
