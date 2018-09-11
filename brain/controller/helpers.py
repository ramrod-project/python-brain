"""
quick helper functions
"""
from . import ADDRESS_KEY, TCP_KEY, UDP_KEY, \
    MOCK_ERROR_DICT, CONFLICT_ERROR_STRING, FIRST_ERROR


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
        msg = CONFLICT_ERROR_STRING.format(field,
                                  common,
                                  interface[ADDRESS_KEY])
        response = MOCK_ERROR_DICT
        response[FIRST_ERROR] = msg
    return response


def has_port_conflict(port_data,
                      existing):
    """

    :param port_data:
    :param existing:
    :return:
    """
    for interface in existing:
        common_tcp = _check_common(TCP_KEY, interface, port_data)
        common_udp = _check_common(UDP_KEY, interface, port_data)
        if common_tcp:
            return common_tcp
        elif common_udp:
            return common_udp
    return None
