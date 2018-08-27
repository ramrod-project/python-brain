"""

"""
from . import EX_PORTS_KEY, IN_PORTS_KEY, PORT_SEPARATOR, \
    ENV_KEY, ENV_SEPARATOR
from . import ALLOWED_PROTOCOLS


def verify_port_map(plugin):
    """
    extra validation /
    PB2 sees empty lists the same as non-existant lists
    :param plugin:
    :return:
    """
    result = True
    ex_ports = plugin.get(EX_PORTS_KEY)
    result &= isinstance(ex_ports, list) and verify_ports(ex_ports)
    in_ports = plugin.get(IN_PORTS_KEY)
    result &= isinstance(in_ports, list) and verify_ports(in_ports)
    env_list = plugin.get(ENV_KEY)
    result &= isinstance(env_list, list) and verify_environment(env_list)
    if result:
        result &= len(ex_ports) == len(in_ports)
    return result


def verify_ports(port_list):
    """
    ports should be of the format
    <int:port_number>/<str:protocol>
    where protocol is either tcp or udp

    :param port_list: <list>
    :return: <bool>
    """
    result = True  # empty list is ok
    for item in port_list:
        try:
            (port, protocol) = item.split(PORT_SEPARATOR)
            port_num = int(port)
        except ValueError:
            result = False
            break
        result &= protocol in ALLOWED_PROTOCOLS
        result &= port == str(port_num)
    return result


def verify_environment(env_list):
    """

    :param env_list: <list>
    :return: <bool>
    """
    result = True  # empty list is ok
    for item in env_list:
        try:
            (key, value) = item.split(ENV_SEPARATOR)
        except ValueError:
            result = False
            break
        result &= bool(key)
        result &= bool(value)
    return result
