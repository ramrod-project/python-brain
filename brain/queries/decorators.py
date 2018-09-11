"""
decorator objects for other functions in the query module
"""
from decorator import decorator
from ..connection import rethinkdb as r, connect
from ..connection import validate_get_dbs


WRAP_RETHINK_ERRORS = (r.errors.ReqlOpFailedError,
                       r.errors.ReqlError,
                       r.errors.ReqlDriverError)


@decorator
def wrap_job_cursor(func_, *args, **kwargs):
    """
    wraps a filter generator.
    Types should be appropriate before passed to rethinkdb

    somewhat specific to the _jobs_cursor function

    :param func_: <callable function>
    :param args: <must have at least 3 arguments>
    :param kwargs:
    :return: returned value from func_
    """
    assert isinstance(args[0], str)
    assert isinstance(args[1], (str, type(None)))
    assert isinstance(args[2], (str, type(None)))
    if args[2] and not args[1]:
        raise ValueError("Must specify location if using port.")
    return func_(*args, **kwargs)


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
    except WRAP_RETHINK_ERRORS as reql_err:
        raise ValueError(str(reql_err))

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
    except WRAP_RETHINK_ERRORS as reql_err:
        raise ValueError(str(reql_err))


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
