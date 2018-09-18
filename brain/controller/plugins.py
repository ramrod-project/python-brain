"""
functions specific to the controller
"""

from time import time
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
from . import ADDRESS_KEY, NAME_KEY, SERVICE_KEY, ID_KEY, ENV_KEY
from . import MOCK_ERROR_DICT, DUPLICATE_SERVICE_STRING, FIRST_ERROR
from . import PLUGIN_STATE_KEY
from .verification import verify_port_map


DEFAULT_LOOKUP_KEY = NAME_KEY


def verify_plugin_contents(plugin):
    """
    extra validation /
    PB2 sees empty lists the same as non-existant lists
    :param plugin:
    :return:
    """
    result = True
    result &= verify_port_map(plugin)
    return result


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
        NAME_KEY: plugin_name
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
                  verify_plugin=True,
                  conn=None):
    """
    :param plugin_data: <dict> dict matching Plugin()
    :param verify_plugin: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb insert response value
    """
    assert isinstance(plugin_data, dict)
    if verify_plugin and not verify(plugin_data, Plugin()):
        raise ValueError("Invalid Plugin entry")
    current = find_plugin(plugin_data[SERVICE_KEY], SERVICE_KEY, conn)
    if not current:
        success = RPC.insert(plugin_data,
                             conflict="update").run(conn)
    else:
        success = MOCK_ERROR_DICT
        error_msg = DUPLICATE_SERVICE_STRING.format(plugin_data[SERVICE_KEY])
        MOCK_ERROR_DICT[FIRST_ERROR] = error_msg
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
                verify_port=True,
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
                  verify_plugin=True,
                  conn=None):
    """

    :param plugin_data: <dict> dict matching Plugin()
    :param verify_plugin: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb update response value
    """

    update_id = plugin_data[ID_KEY]
    original = get(update_id, conn=conn)
    success = RPC.get(update_id).update(plugin_data).run(conn)
    if verify_plugin:
        updated = get(update_id, conn=conn)
        if not verify(updated, Plugin()):
            success = RPC.get(update_id).update(original).run(conn)
            raise ValueError("Invalid Plugin entry {}".format(success))
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
    new_kv = "{}=restart".format(int(time()))
    return RPC.get(plugin_id)\
        .update(
            {DESIRED_STATE_KEY: desired_state,
             ENV_KEY: r.row[ENV_KEY].prepend(new_kv)
            })\
        .run(conn)


@wrap_rethink_errors
@wrap_connection
def recover_state(serv_name, conn=None):
    """

    :param serv_name: <str> service name of plugin
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dictionary> last plugin state
    """
    serv_filter = {SERVICE_KEY: serv_name}
    curs = RPC.filter(serv_filter).run(conn)
    num_docs = 0
    for doc in curs:
        num_docs += 1
    if num_docs != 1:
        raise ValueError("Duplicate Services found when recovering")
    return doc[PLUGIN_STATE_KEY]


@wrap_rethink_errors
@wrap_connection
def record_state(serv_name, state, conn=None):
    """
    MAKE A DOCSTRING
    :param serv_name: <str> service name of plugin instance
    :param state: <dictionary> plugin state
    :param conn: <rethinkdb.DefaultConnection>
    :return: 
    """
    serv_filter = {SERVICE_KEY:serv_name}
    updated = {PLUGIN_STATE_KEY: state}
    return RPC.filter(serv_filter).update(updated).run(conn)


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
