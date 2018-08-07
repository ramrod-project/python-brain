"""
functions specific to the controller
"""

from ..queries.decorators import wrap_rethink_errors, wrap_connection
from ..queries import RPC, RPP
from .. import r
from ..checks import verify
from ..brain_pb2 import Plugin, Port
from .decorators import expect_arg_type
from . import DESIRE_ACTIVE, DESIRE_STOP, DESIRE_RESTART
from . import DESIRED_STATE_KEY, ALLOWED_DESIRED_STATES
from . import ADDRESS_KEY, NAME_KEY


def _check_common(field, interface, port_data):
    """

    :param field:
    :param interface:
    :param port_data:
    :return:
    """
    response = {}
    common = list(set(port_data[field]) &
                  set(interface[field]))
    if common:
        msg = "{} conflicts(s): {} in use on {}".format(field,
                                                        common,
                                                        interface['Address'])
        response = {"errors": 1,
                    "first_error": msg}
    return response


def has_port_conflict(port_data,
                      existing):
    """

    :param port_data:
    :param existing:
    :return:
    """
    for interface in existing:
        common_tcp = _check_common("TCPPorts", interface, port_data)
        common_udp = _check_common("UDPPorts", interface, port_data)
        if common_tcp:
            return common_tcp
        elif common_udp:
            return common_udp
    return None


@wrap_rethink_errors
@wrap_connection
def get_plugin_by_name(plugin_name,
                       conn=None):
    """

    :param plugin_name: <str> name of plugin
    :param conn: <rethinkdb.DefaultConnection>
    :return: <list> rethinkdb cursor
    """
    result = RPC.filter({
        "Name": plugin_name
    }).run(conn)
    return result


@wrap_rethink_errors
@wrap_connection
def get_plugins(conn=None):
    """
    :param conn: <rethinkdb.DefaultConnection>
    :return: <list>
    """
    return list(RPC.run(conn))


def get_names(conn=None):
    """

    :param conn:
    :return: <list> of <str>
    """
    return list(set([x[NAME_KEY] for x in get_plugins(conn=conn)]))


@wrap_rethink_errors
@wrap_connection
def get_ports_by_ip(ip_address,
                    conn=None):
    """

    :param ip_address: <str> name of interface
    :param conn: <rethinkdb.DefaultConnection>
    :return: <list> rethinkdb cursor
    """
    if ip_address == "":
        result = RPP.filter({
            "Address": ip_address
        }).run(conn)
    else:
        result = RPP.filter(
            (r.row["Address"] == ip_address) |
            (r.row["Address"] == "")
        ).run(conn)
    return result


@wrap_rethink_errors
@wrap_connection
def create_plugin(plugin_data,
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
    current = get_plugin_by_name(
        plugin_data["Name"],
        conn=conn
    )
    try:
        current.next()
        return {
            "errors": 1,
            "first_error": "Plugin {} exists!".format(plugin_data['Name'])
        }
    except r.ReqlCursorEmpty:
        pass
    success = RPC.insert(plugin_data,
                         conflict="update").run(conn)
    return success


def _get_existing_interface(existing, port_data):
    """

    :param existing: <list>
    :param port_data:  <dict>
    :return: interface or None
    """
    interface_existing = None
    for interface in existing:
        if interface["Address"] == port_data["Address"]:
            interface_existing = interface
    return interface_existing


@expect_arg_type(expected=(dict, ))
@wrap_rethink_errors
@wrap_connection
def create_port(port_data,
                verify_port=False,
                conn=None):
    """

    :param port_data: <dict> dict matching Port()
    :param verify_port: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb insert response value
    """
    if verify_port and not verify(port_data, Port()):
        raise ValueError("Invalid Port entry")
    existing = list(get_ports_by_ip(port_data["Address"], conn=conn))
    conflicts = has_port_conflict(port_data, existing)
    if conflicts:
        return conflicts
    interface_existing = _get_existing_interface(existing, port_data)
    if not interface_existing:
        success = RPP.insert(
            port_data,
            conflict="update"
        ).run(conn)
    else:
        combined_tcp = port_data["TCPPorts"] + interface_existing["TCPPorts"]
        interface_existing["TCPPorts"] = list(set(combined_tcp))
        combined_udp = port_data["UDPPorts"] + interface_existing["UDPPorts"]
        interface_existing["UDPPorts"] = list(set(combined_udp))
        success = RPP.get(interface_existing["id"]).update({
            "TCPPorts": interface_existing["TCPPorts"],
            "UDPPorts": interface_existing["UDPPorts"]
        }).run(conn)
    return success


@wrap_rethink_errors
@wrap_connection
def get_interfaces(conn=None):
    """

    :param conn:
    :return:
    """
    res = RPP.pluck([ADDRESS_KEY]).run(conn)
    return list(set([x[ADDRESS_KEY] for x in res]))  # unique list


@expect_arg_type(expected=(dict, ))
@wrap_rethink_errors
@wrap_connection
def update_plugin(plugin_data,
                  verify_plugin=False,
                  conn=None):
    """

    :param plugin_data: <dict> dict matching Plugin()
    :param verify_plugin: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb update response value
    """
    if verify_plugin and not verify(plugin_data, Plugin()):
        raise ValueError("Invalid Plugin entry")
    current = get_plugin_by_name(plugin_data["Name"], conn=conn)
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


@wrap_rethink_errors
@wrap_connection
def get(plugin_id, conn=None):
    """

    :param plugin_id:
    :param conn:
    :return:
    """
    return RPC.get(plugin_id).run(conn)


@wrap_rethink_errors
@wrap_connection
def quick_change_desired_state(plugin_id, desired_state, conn=None):
    """

    :param plugin_id:
    :param desired_state:
    :param conn:
    :return:
    """
    assert desired_state in ALLOWED_DESIRED_STATES
    desired = {DESIRED_STATE_KEY: desired_state}
    return RPC.get(plugin_id).update(desired).run(conn)


def activate(plugin_id, conn=None):
    """

    :param plugin_id:
    :param conn:
    :return:
    """
    return quick_change_desired_state(plugin_id,
                                      DESIRE_ACTIVE,
                                      conn=conn)


def restart(plugin_id, conn=None):
    """

    :param plugin_id:
    :param conn:
    :return:
    """
    return quick_change_desired_state(plugin_id,
                                      DESIRE_RESTART,
                                      conn=conn)


def stop(plugin_id, conn=None):
    """

    :param plugin_id:
    :param conn:
    :return:
    """
    return quick_change_desired_state(plugin_id,
                                      DESIRE_STOP,
                                      conn=conn)
