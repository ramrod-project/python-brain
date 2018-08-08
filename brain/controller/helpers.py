"""
quick helper functions
"""


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