"""
code to interact with the (misnomer)
r.Controller.Ports table
"""

from .. import r
from ..queries.decorators import wrap_connection, wrap_rethink_errors
from ..queries import RPP
from ..checks import verify
from ..brain_pb2 import Port
from .helpers import has_port_conflict, _check_common
from .decorators import expect_arg_type
from . import ADDRESS_KEY, UDP_KEY, TCP_KEY, CONFLICT_ACTION, ID_KEY


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
            ADDRESS_KEY: ip_address
        }).run(conn)
    else:
        result = RPP.filter(
            (r.row[ADDRESS_KEY] == ip_address) |
            (r.row[ADDRESS_KEY] == "")
        ).run(conn)
    return result


@wrap_rethink_errors
@wrap_connection
def get_interfaces(conn=None):
    """

    :param conn:
    :return:
    """
    res = RPP.pluck([ADDRESS_KEY]).run(conn)
    return list(set([x[ADDRESS_KEY] for x in res]))  # unique list


def _get_existing_interface(existing, port_data):
    """

    :param existing: <list>
    :param port_data:  <dict>
    :return: interface or None
    """
    interface_existing = None
    for interface in existing:
        if interface[ADDRESS_KEY] == port_data[ADDRESS_KEY]:
            interface_existing = interface
    return interface_existing


@expect_arg_type(expected=(dict, ))
@wrap_rethink_errors
@wrap_connection
def create_port(port_data,
                verify_port=True,
                conn=None):
    """

    :param port_data: <dict> dict matching Port()
    :param verify_port: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb insert response value
    """
    if verify_port and not verify(port_data, Port()):
        raise ValueError("Invalid Port entry")
    existing = list(get_ports_by_ip(port_data[ADDRESS_KEY], conn=conn))
    conflicts = has_port_conflict(port_data, existing)
    if conflicts:
        return conflicts
    interface_existing = _get_existing_interface(existing, port_data)
    if not interface_existing:
        success = RPP.insert(
            port_data,
            conflict=CONFLICT_ACTION
        ).run(conn)
    else:
        combined_tcp = port_data[TCP_KEY] + interface_existing[TCP_KEY]
        interface_existing[TCP_KEY] = list(set(combined_tcp))
        combined_udp = port_data[UDP_KEY] + interface_existing[UDP_KEY]
        interface_existing[UDP_KEY] = list(set(combined_udp))
        success = RPP.get(interface_existing[ID_KEY]).update({
            TCP_KEY: interface_existing[TCP_KEY],
            UDP_KEY: interface_existing[UDP_KEY]
        }).run(conn)
    return success
