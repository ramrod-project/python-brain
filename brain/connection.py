from time import sleep, time
from uuid import uuid4
import rethinkdb
from decorator import decorator
from rethinkdb.net import DefaultConnection
from .environment import check_stage_env

#Recursive imports at bottom of file

BRAIN_DB = "Brain"
AUDIT_DB = "Audit"
PLUGINDB = "Plugins"
JOBS = "Jobs"
TARGETS = "Targets"
OUTPUTS = "Outputs"
SELF_TEST = {BRAIN_DB: [JOBS, TARGETS, OUTPUTS],
             #AUDIT_DB: [], #Audit DB soon into latest
             PLUGINDB: []}

DEFAULT_HOSTS = {"PROD": "rethinkdb",
                 "QA": "rethinkdb",
                 "DEV": "localhost",
                 "TESTING": "localhost",
                 "": "localhost", #environment not configured, try anyway
                 }

@decorator
def wrap_self_test(f, *args, **kwargs):
    """
    should be applied as decorator to functions
    requiring a SELF_TEST dict

    If the caller does not supply a self_test dict, it supplies one

    :param f: <function>
    :param args: <tuple> positional arguments
    :param kwargs: <dict> keyword arguments
    :return: return value of the called function
    """
    if not args[-1]:
        new_args = list(args)
        new_args[-1] = SELF_TEST
        args = tuple(new_args)
    return f(*args, **kwargs)


class BrainNotReady(Exception):
    """
    Simple exception to identify that the brain is not ready for use at this time
    """
    pass


def validate_brain(connection, requirements=None):
    """
    Alias to brain_post function

    Checks that the brain is appropriately seeded and ready for use.

    Raises AssertionError's if the brain is not ready.

    :param connection:  <rethinkdb.net.DefaultConnection>
    :param requirements:<dict> keys=Required Databases, key-values=Required Tables in each database
    :return: <rethinkdb.net.DefaultConnection> if verified
    """
    return brain_post(connection, requirements)

@wrap_self_test
def brain_post(connection, requirements=None):
    """
    Power On Self Test for the brain.

    Checks that the brain is appropriately seeded and ready for use.

    Raises AssertionError's if the brain is not ready.

    :param connection:  <rethinkdb.net.DefaultConnection>
    :param requirements:<dict> keys=Required Databases, key-values=Required Tables in each database
    :return: <rethinkdb.net.DefaultConnection> if verified
    """
    assert isinstance(connection, DefaultConnection)
    remote_dbs = set([x for x in rethinkdb.db_list().run(connection)])
    for database in requirements:
        assert (database in remote_dbs), "database {} must exist".format(database)
        remote_tables = frozenset([x for x in rethinkdb.db(database).table_list().run(connection)])
        for table in requirements[database]:
            assert (table in remote_tables), "{} must exist in {}".format(table, database)
    test_table = "test_table_{}".format(uuid4()).replace("-", "")   # '-' is not valid
    create_plugin(test_table, connection)
    RPX.table(test_table).insert({"test": "data"}).run(connection)
    destroy_plugin(test_table, connection)
    return connection

def connect(host=None,
            port=rethinkdb.DEFAULT_PORT,
            timeout=20,
            verify=True,
            **kwargs):
    """
    RethinkDB semantic connection wrapper

    raises <brain.connection.BrainNotReady> if connection verification fails

    :param verify: <bool> (default True) whether to run POST
    :param timeout: <int> max time (s) to wait for connection
    :param kwargs:  <dict> passthrough rethinkdb arguments
    :return:
    """
    if not host:
        host = DEFAULT_HOSTS.get(check_stage_env())
    connection = None
    tries = 0
    time_quit = time() + timeout
    while not connection and time() <= time_quit:
        tries += 1
        connection = _attempt_connect(host, port, timeout/3, verify, **kwargs)
        if not connection:
            sleep(0.5)
    if not connection:
        raise BrainNotReady(
            "Tried ({}:{}) {} times at {} second max timeout".format(host,
                                                                     port,
                                                                     tries,
                                                                     timeout))
    return connection


def _attempt_connect(host, port, timeout, verify, **kwargs):
    """
    Internal function to attempt
    :param host: <str> "localhost" or IPAddress
    :param port: <int>
    :param timeout: <int>
    :param verify: <bool>
    :param kwargs: <**dict> rethinkdb keyword args
    :return: <connection> or <NoneType>
    """
    try:
        connection = rethinkdb.connect(host,
                                       port,
                                       timeout=timeout,
                                       **kwargs)
        if verify:
            brain_post(connection)
    except (rethinkdb.errors.ReqlDriverError,
            rethinkdb.errors.ReqlOpFailedError,
            AssertionError):
        connection = None
    return connection

#RecursiveImports
from .queries import create_plugin, destroy_plugin, RPX
