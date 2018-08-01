"""
decorators for controller specific functions
"""

from decorator import decorator


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