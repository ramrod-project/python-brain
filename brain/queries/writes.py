"""
assortment of wrapped queries
"""
from ..brain_pb2 import Jobs, Target, Commands
from ..checks import verify
from .decorators import wrap_connection
from .decorators import wrap_rethink_errors
from . import RPX, RBT, RBJ
from .reads import plugin_exists


@wrap_rethink_errors
@wrap_connection
def insert_new_target(plugin_name, location_num,
                      port_num=0, optional="",
                      verify_target=False, conn=None):
    """
    insert_new_target function gets called when the user's input is validated
    and inserts a new target to Brain.Targets table.
    :param plugin_name: <str> user input plugin name
    :param location_num: <str> user input location number
    :param port_num: <str> user input port number
    :param optional: <str> user input optional
    :return: <dict> rethinkdb insert response value
    """
    target = {"PluginName": str(plugin_name),
              "Location": str(location_num),
              "Port": str(port_num),
              "Optional": {"init": str(optional)}}
    return insert_target(target, verify_target, conn)

@wrap_rethink_errors
@wrap_connection
def insert_target(target, verify_target=False,
                  conn=None):
    """

    :param target:  <dict> of Target() format
    :param verify_target: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb insert response value
    """
    if verify_target and not verify(target, Target()):
        raise ValueError("Invalid Target")
    return RBT.insert([target]).run(conn)

@wrap_rethink_errors
@wrap_connection
def insert_jobs(jobs, verify_jobs=True, conn=None):
    """
    insert_jobs function inserts data into Brain.Jobs table

    jobs must be in Job format

    :param jobs: <list> of Jobs
    :return: <dict> rethinkdb insert response value
    """
    assert isinstance(jobs, list)
    if verify_jobs and not verify({"Jobs": jobs}, Jobs()):
        raise ValueError("Invalid Jobs")
    inserted = RBJ.insert(jobs).run(conn)
    return inserted


@wrap_rethink_errors
@wrap_connection
def create_plugin(plugin_name, conn=None):
    """
    Creates a new plugin

    :param plugin_name: <str>
    :param conn:
    :return: <bool> successfully inserted
    """
    if not plugin_exists(plugin_name, conn=conn):
        RPX.table_create(plugin_name,
                         primary_key="CommandName"
                         ).run(conn)
    return True


@wrap_rethink_errors
@wrap_connection
def destroy_plugin(plugin_name, conn=None):
    """
    Creates a new plugin

    :param plugin_name: <str>
    :param conn:
    :return: <bool> successfully inserted
    """
    if plugin_exists(plugin_name, conn=conn):
        RPX.table_drop(plugin_name,
                       ).run(conn)
    return True


@wrap_rethink_errors
@wrap_connection
def advertise_plugin_commands(plugin_name, commands,
                              verify_commands=False,
                              conn=None):
    """

    :param plugin_name:
    :param commands:
    :param verify_commands:
    :param conn:
    :return:
    """
    assert isinstance(commands, list)
    if verify_commands and not verify({"Commands": commands},
                                      Commands()):
        raise ValueError("Invalid Commands")
    success = RPX.table(plugin_name).insert(commands,
                                            conflict="update"
                                            ).run(conn)
    return success
