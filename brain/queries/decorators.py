"""
decorator objects for other functions in the query module
"""

from ..connection import rethinkdb as r, connect
from ..connection import validate_get_dbs
from decorator import decorator

WRAP_RETHINK_ERRORS = (r.errors.ReqlOpFailedError,
                       r.errors.ReqlError,
                       r.errors.ReqlDriverError)


@decorator
def wrap_rethink_errors(func_, *args, **kwargs):
    """
    Wraps rethinkdb specific errors as builtin/Brain errors

    :param func_: <function> to call
    :param args:  <tuple> positional arguments
    :param kwargs: <dict> keyword arguments
    :return: inherits from the called function
    """
    try:
        return func_(*args, **kwargs)
    except WRAP_RETHINK_ERRORS as e:
        raise ValueError(str(e))

@decorator
def wrap_rethink_generator_errors(func_, *args, **kwargs):
    """

    :param func_: <function> to call
    :param args:  <tuple> positional arguments
    :param kwargs: <dict> keyword arguments
    :return: inherits from the called function
    """
    try:
        for data in func_(*args, **kwargs):
            yield data
    except WRAP_RETHINK_ERRORS as e:
        raise ValueError(str(e))


@decorator
def wrap_connection_reconnect_test(func_, *args, **kwargs):
    """
    if a connection argument is passed, verify connection is good
    if not connected, attempt reconnect
    if reconnect fails, raises the rethink error
    other decorator will translate to standard error

    note: <rethinkdb.DefaultConnection>.is_open() appears to hang
            when the database is pulled out from under conn obj

    should be decorated prior to wrap_connection

    :param func_: <function> to call
    :param args:  <tuple> positional arguments
    :param kwargs: <dict> keyword arguments
    :return:
    :raises: ReqlDriverError or ConnectionRefusedError if reconnect failed.
    """
    conn = args[-1]
    if conn:  # conn object attempted
        try:
            validate_get_dbs(conn)
        except WRAP_RETHINK_ERRORS:
            conn.reconnect()  #throw may occur here
    return func_(*args, **kwargs)


@decorator
@wrap_connection_reconnect_test
def wrap_connection(func_, *args, **kwargs):
    """
    conn (connection) must be the last positional argument
    in all wrapped functions

    :param func_: <function> to call
    :param args:  <tuple> positional arguments
    :param kwargs: <dict> keyword arguments
    :return:
    """
    if not args[-1]:
        new_args = list(args)
        new_args[-1] = connect()
        args = tuple(new_args)
    return func_(*args, **kwargs)
