"""
assortment of wrapped queries
"""
from ..brain_pb2 import Jobs, Target, Commands, Plugin, Port
from ..checks import verify
from ..connection import rethinkdb as r
from .decorators import wrap_connection
from .decorators import wrap_rethink_errors
from . import RPX, RBT, RBJ, RPC, RPP
from .reads import plugin_exists, get_plugin_by_name_controller, get_ports_by_ip_controller


def _check_port_conflict(port_data,
                         existing):
    for interface in existing:
        common_tcp = list(set(port_data["TCPPorts"]) &
                      set(interface["TCPPorts"]))
        if common_tcp != []:
            return {
                "errors": 1,
                "first_error": "TCP Port conflict(s): \
                {} in use on {}"
                .format(
                    common_tcp,
                    interface["Address"]
                )
            }
        common_udp = list(set(port_data["UDPPorts"]) &
                      set(interface["UDPPorts"]))
        if common_udp != []:
            return {
                "errors": 1,
                "first_error": "UDP Port conflict(s): \
                {} in use on {}"
                .format(
                    common_udp,
                    interface["Address"]
                )
            }
    return None


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


@wrap_rethink_errors
@wrap_connection
def create_plugin_controller(plugin_data,
                              verify_commands=False,
                              conn=None):
    """

    :param plugin_data: <dict> dict matching Plugin()
    :param verify_commands: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb insert response value
    """
    assert isinstance(plugin_data, dict)
    if verify_commands and not verify(plugin_data, Plugin()):
        raise ValueError("Invalid Plugin entry")
    current = get_plugin_by_name_controller(
        plugin_data["Name"],
        conn=conn
    )
    try:
        current.next()
        return {
            "errors": 1,
            "first_error": "".join([
                "Plugin ",
                plugin_data["Name"],
                " exists!"
            ])
        }
    except r.ReqlCursorEmpty:
        pass
    success = RPC.insert(plugin_data,
                         conflict="update"
                         ).run(conn)
    return success


@wrap_rethink_errors
@wrap_connection
def create_port_controller(port_data,
                           verify_port=False,
                           conn=None):
    """

    :param port_data: <dict> dict matching Port()
    :param verify_port: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb insert response value
    """
    assert isinstance(port_data, dict)
    if verify_port and not verify(port_data, Port()):
        raise ValueError("Invalid Port entry")
    existing = list(get_ports_by_ip_controller(
        port_data["Address"],
        conn=conn
    ))
    conflicts = _check_port_conflict(port_data, existing)
    if conflicts:
        return conflicts
    interface_existing = None
    for interface in existing:
        if interface["Address"] == port_data["Address"]:
            interface_existing = interface
    if not interface_existing:
        success = RPP.insert(
            port_data,
            conflict="update"
        ).run(conn)
    else:
        interface_existing["TCPPorts"] = list(set(port_data["TCPPorts"] + interface_existing["TCPPorts"]))
        interface_existing["UDPPorts"] = list(set(port_data["UDPPorts"] + interface_existing["UDPPorts"]))
        success = RPP.get(interface_existing["id"]).update({
            "TCPPorts": interface_existing["TCPPorts"],
            "UDPPorts": interface_existing["UDPPorts"]
        }).run(conn)
    return success


@wrap_rethink_errors
@wrap_connection
def update_plugin_controller(plugin_data,
                             verify_plugin=False,
                             conn=None):
    """

    :param plugin_data: <dict> dict matching Plugin()
    :param verify_commands: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb update response value
    """
    assert isinstance(plugin_data, dict)
    if verify_plugin and not verify(plugin_data, Plugin()):
        raise ValueError("Invalid Plugin entry")
    current = get_plugin_by_name_controller(
        plugin_data["Name"],
        conn=conn
    )
    update_id = None
    try:
        update_id = current.next()["id"]
    except r.ReqlCursorEmpty:
        return {
            "errors": 1,
            "first_error": "Cannot update non-existent plugin!"
        }
    success = RPC.get(update_id).update(plugin_data).run(conn)
    return success
