from time import sleep
import rethinkdb
from .environment import check_stage_env
from rethinkdb.net import DefaultConnection
from time import time


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
                 "DEV": "rethinkdb_testing",
                 "TESTING": "localhost",
                 "": "localhost", #environment not configured, try anyway
                }


class BrainNotReady(Exception):
    """
    Simple exception to identify that the brain is not ready for use at this time
    """
    pass



def brain_post(connection, requirements=SELF_TEST):
    """
    Power On Self Test for the brain.

    Checks that the brain is appropriately seeded and ready for use.

    Raises AssertionError's if the brain is not ready.

    :param connection:  <rethinkdb.net.DefaultConnection>
    :param requirements:<dict> keys=Required Databases, key-values=Required Tables in each database
    :return: <None>
    """
    remote_dbs = [x for x in rethinkdb.db_list().run(connection)]
    for database in requirements:
        assert (database in remote_dbs), "database {} must exist".format(database)
        remote_tables = frozenset([x for x in rethinkdb.db(database).table_list().run(connection)])
        for table in requirements[database]:
            assert (table in remote_tables), "{} must exist in {}".format(table, database)

def connect(verify=True,
            host=None,
            port=rethinkdb.DEFAULT_PORT,
            timeout=20,
            **kwargs):
    """
    RethinkDB semantic connection wrapper

    raises <brain.connection.BrainNotReady> if connection verification fails

    :param verify: <bool> (default True) whether to run POST
    :param timeout: <int> max time (s) to wait for connection
    :param kwargs:  <dict> passthrough rethinkdb arguments
    :return:
    """
    host = DEFAULT_HOSTS.get(check_stage_env())
    connection = None
    tries = 0
    time_quit = time() + timeout
    while not connection and time() <= time_quit:
        tries += 1
        try:
            connection = rethinkdb.connect(host,
                                           port,
                                           timeout=timeout/3,
                                           **kwargs)
            if verify:
                brain_post(connection)
        except (rethinkdb.errors.ReqlDriverError, AssertionError):
            connection = None
        if not connection:
            sleep(0.5)
    if not connection:
        raise BrainNotReady("BrainNotReady: Tried {} times at {} second max timeout".format(tries, timeout))
    return connection

