"""
Read telemetry from target
"""

from ..static import r, RBT, PLUGIN_NAME_KEY, PORT_FIELD, \
    LOCATION_FIELD, ID_FIELD
from ..queries.decorators import wrap_rethink_errors, wrap_connection


def target_query(plugin, port, location):
    """
    prepared ReQL for target
    """
    return ((r.row[PLUGIN_NAME_KEY] == plugin) &
            (r.row[PORT_FIELD] == port) &
            (r.row[LOCATION_FIELD] == location))


@wrap_rethink_errors
@wrap_connection
def get_target(plugin, port, location, conn=None):
    """

    :param plugin:
    :param port:
    :param location:
    :param conn:
    :return: <str> id of the job
    """
    query = target_query(plugin, port, location)
    cur = RBT.filter(query).limit(1).run(conn)
    output = None
    for doc in cur:
        output = doc  # forces the cursor dereference
    return output


def get_target_id(plugin, port, location, conn=None):
    return get_target(plugin, port, location, conn).get(ID_FIELD)
