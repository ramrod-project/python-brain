"""
decorators for controller specific functions
"""

from decorator import decorator
from . import ID_KEY, SERVICE_KEY, FIRST_ERROR, UNKNOWN_PLUGIN_STRING, MOCK_ERROR_DICT

@decorator
def expect_arg_type(func_, expected=None,
                    *args, **kwargs):
    """

    :param func_:
    :param expected:
    :param args:
    :param kwargs:
    :return:
    """
    assert isinstance(expected, tuple)
    for arg_idx in range(len(expected)):
        assert isinstance(args[arg_idx], expected[arg_idx])
    return func_(*args, **kwargs)


@decorator
def set_plugin_id(func_, *args, **kwargs):
    """

    :param func_:
    :param args:
    :param kwargs:
    :return:
    """
    from .plugins import find_plugin  # load time workaround- JIT import
    plugin = args[0]
    plugin_id = plugin.get(ID_KEY, False)
    service_name = plugin.get(SERVICE_KEY, False)
    if not plugin_id:
        found_plugin = find_plugin(service_name, SERVICE_KEY, args[-1])
        if found_plugin:
            plugin[ID_KEY] = found_plugin[-1][ID_KEY]
        else:
            invalid_plugin = MOCK_ERROR_DICT
            invalid_plugin[FIRST_ERROR] = UNKNOWN_PLUGIN_STRING
            return invalid_plugin
    return func_(*args, **kwargs)



