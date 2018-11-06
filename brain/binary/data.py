"""
functions related to moving binary objects in/out of Brain.Files
"""

from time import time
from .. import r
from ..queries.decorators import wrap_connection, wrap_rethink_errors
from ..queries.decorators import wrap_connection_reconnect_test
from ..checks import verify
from ..brain_pb2 import Binary
from ..queries import RBF
from .decorators import wrap_name_to_id, wrap_guess_content_type
from .decorators import wrap_content_as_binary_if_needed
from .decorators import wrap_split_big_content
from . import PRIMARY_FIELD, CONTENT_FIELD, TIMESTAMP_FIELD
from . import PART_FIELD, PARTS_FIELD, PARENT_FIELD

BINARY = r.binary


@wrap_rethink_errors
@wrap_connection_reconnect_test
@wrap_connection
@wrap_name_to_id
@wrap_guess_content_type
@wrap_split_big_content
@wrap_content_as_binary_if_needed
def put(obj_dict, conn=None, **kwargs):
    """
    This function might thorw an error like:
        Query size (290114573) greater than maximum (134217727)
    caller may need to manually split files at this time
    :param obj_dict: <dict> matching brain_pb2.Binary object
    :param conn:
    :param kwargs:
    :return:
    """
    if kwargs.get("verify", False):
        verify(obj_dict, Binary())
    inserted = RBF.insert(obj_dict).run(conn)
    return inserted


def put_buffer(filename, content, conn=None):
    """
    helper function for put
    :param filename: <str>
    :param content: <bytes>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict>
    """
    obj_dict = {PRIMARY_FIELD: filename,
                CONTENT_FIELD: content,
                TIMESTAMP_FIELD: time()}
    return put(obj_dict, conn=conn)


@wrap_rethink_errors
@wrap_connection
def get(filename, conn=None):
    """

    :param filename:
    :param conn:
    :return: <dict>
    """
    res_file = RBF.get(filename).run(conn)
    full_content = b""
    try:
        for part in res_file[PARTS_FIELD]:
            part_file = RBF.get(part).run(conn)
            full_content += part_file[CONTENT_FIELD]

        res_file[CONTENT_FIELD] = full_content
    except KeyError:
        return res_file
    return res_file


@wrap_rethink_errors
@wrap_connection
def list_dir(conn=None):
    """

    :param conn:
    :return: <list>
    """
    available = RBF.filter({PART_FIELD: False}).pluck(PRIMARY_FIELD).run(conn)
    return [x[PRIMARY_FIELD] for x in available]


@wrap_rethink_errors
@wrap_connection
def delete(filename, conn=None):
    """
    deletes a file
    filename being a value in the "id" key
    :param filename: <str>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict>
    """
    return RBF.filter((r.row[PRIMARY_FIELD] == filename) | (r.row[PARENT_FIELD] == filename)).delete().run(conn)
