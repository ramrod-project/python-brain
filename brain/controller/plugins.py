"""
functions specific to the controller
"""

from ..queries.decorators import wrap_rethink_errors, wrap_connection
from ..queries import RPC, RPP
from .. import r
from ..decorators import deprecated_function
from ..checks import verify
from ..brain_pb2 import Plugin, Port
from .decorators import expect_arg_type, set_plugin_id
from .helpers import _check_common, has_port_conflict
from .interfaces import get_ports_by_ip
from . import DESIRE_ACTIVE, DESIRE_STOP, DESIRE_RESTART
from . import DESIRED_STATE_KEY, ALLOWED_DESIRED_STATES
from . import ADDRESS_KEY, NAME_KEY, SERVICE_KEY, ID_KEY


DEFAULT_LOOKUP_KEY = "Name"


@deprecated_function(replacement="brain.controller.plugins.find_plugin")
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
def find_plugin(value,
                key=DEFAULT_LOOKUP_KEY,
                conn=None):
    """
    get's the plugin matching the key and value

    example: find_plugin("plugin1", "ServiceName") => list of 0 or 1 item
    example: find_plugin("plugin1", "Name") => list of 0-to-many items

    :param value:
    :param key: <str> (default "Name")
    :param conn:
    :return:
    """
    # cast to list to hide rethink internals from caller
    result = list(RPC.filter({
        key: value
    }).run(conn))
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
    current = find_plugin(plugin_data[SERVICE_KEY], SERVICE_KEY, conn)
    if not current:
        success = RPC.insert(plugin_data,
                             conflict="update").run(conn)
    else:
        success = {
            "errors": 1,
            "first_error": "Duplicate service name exists {}".format(
                plugin_data[SERVICE_KEY])}
    return success


@deprecated_function(replacement=
                     "brain.controller.interfaces._get_existing_interface")
def _get_existing_interface(existing, port_data):
    """

    :param existing: <list>
    :param port_data:  <dict>
    :return: interface or None
    """
    from .interfaces import _get_existing_interface as _new_gei
    return _new_gei(existing, port_data)


@deprecated_function(replacement="brain.controller.interfaces.create_port")
def create_port(port_data,
                verify_port=False,
                conn=None):
    """

    :param port_data: <dict> dict matching Port()
    :param verify_port: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb insert response value
    """
    from .interfaces import create_port as new_create_port
    return new_create_port(port_data, verify_port=verify_port, conn=conn)


@deprecated_function(replacement="brain.controller.interfaces.get_interfaces")
def get_interfaces(conn=None):
    """

    :param conn:
    :return:
    """
    from .interfaces import get_interfaces as new_get_interfaces
    return new_get_interfaces(conn=conn)


@expect_arg_type(expected=(dict, ))
@wrap_rethink_errors
@wrap_connection
@set_plugin_id
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
    update_id = plugin_data[ID_KEY]
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
