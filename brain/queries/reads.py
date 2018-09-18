"""
assortment of wrapped queries
"""
from time import time
from ..brain_pb2 import Job
from ..checks import verify
from ..connection import rethinkdb as r
from ..decorators import deprecated_function
from ..static import RPX, RBT, RBJ, RBO, COMMAND_NAME_KEY, LOCATION_FIELD, \
    PLUGIN_NAME_KEY, STATUS_FIELD, READY, TARGET_FIELD, START_FIELD, DONE, \
    ID_FIELD, OUTPUTJOB_FIELD, CONTENT_FIELD, EXPIRE_FIELD, PORT_FIELD
from . import CUSTOM_FILTER_NAME
from .decorators import wrap_connection
from .decorators import wrap_rethink_generator_errors
from .decorators import wrap_rethink_errors
from .decorators import wrap_job_cursor


@wrap_job_cursor
def _jobs_cursor(plugin_name, location=None, port=None, custom=None):
    """
    generates a reql cursor for plugin_name
    with status ready
    and prepares to sort by StartTime
    :param plugin_name:
    :param location:
    :param port:
    :return:
    """
    cur = RBJ.get_all(READY, index=STATUS_FIELD)
    cur_filter = (r.row[TARGET_FIELD][PLUGIN_NAME_KEY] == plugin_name)
    cur_filter = cur_filter & \
                 (~r.row.has_fields(EXPIRE_FIELD) |
                  r.row[EXPIRE_FIELD].ge(time()))
    if location:
        cur_filter = cur_filter & \
                     (r.row[TARGET_FIELD][LOCATION_FIELD] == location)
    if port:
        cur_filter = cur_filter & \
                     (r.row[TARGET_FIELD][PORT_FIELD] == port)
    if custom:
        cur_filter = cur_filter & custom
    return cur.filter(cur_filter).order_by(START_FIELD)


@wrap_rethink_generator_errors
@wrap_connection
def get_targets(conn=None):
    """
    get_brain_targets function from Brain.Targets table.

    :return: <generator> yields dict objects
    """
    targets = RBT
    results = targets.run(conn)
    for item in results:
        yield item


@wrap_rethink_generator_errors
@wrap_connection
def get_targets_by_plugin(plugin_name, conn=None):
    """
    get_targets_by_plugin function from Brain.Targets table

    :return: <generator> yields dict objects
    """
    targets = RBT
    results = targets.filter({PLUGIN_NAME_KEY: plugin_name}).run(conn)
    for item in results:
        yield item


@wrap_rethink_generator_errors
@wrap_connection
def get_plugin_commands(plugin_name, conn=None):
    """
    get_specific_commands function queries Plugins.<PluginName> table
    the plugin name will be based off the user selection from the ui.
    It will return the query onto w2 as a dictionary nested in a list.

    :param plugin_name: <str> user's plugin selection
    :return: <generator> yields dictionaries
    """
    results = RPX.table(plugin_name).order_by(COMMAND_NAME_KEY).run(conn)
    for item in results:
        yield item


@wrap_rethink_errors
@wrap_connection
def get_plugin_command(plugin_name, command_name, conn=None):
    """
    get_specific_command function queries a specific CommandName

    :param plugin_name: <str> PluginName
    :param command_name: <str> CommandName
    :return: <dict>
    """
    commands = RPX.table(plugin_name).filter(
        {COMMAND_NAME_KEY: command_name}).run(conn)
    command = None
    for command in commands:
        continue  # exhausting the cursor
    return command


@wrap_rethink_errors
@wrap_connection
def get_job_status(job_id, conn=None):
    """

    :param job_id: <str>
    :param conn: <RethinkDefaultConnection>
    :return:
    """
    job = RBJ.get(job_id).pluck(STATUS_FIELD).run(conn)
    return job[STATUS_FIELD]


@wrap_rethink_errors
@wrap_connection
def is_job_done(job_id, conn=None):
    """
    is_job_done function checks to if Brain.Jobs Status is 'Done'

    :param job_id: <str> id for the job
    :param conn: (optional)<connection> to run on
    :return: <dict> if job is done <false> if
    """
    result = False
    get_done = RBJ.get_all(DONE, index=STATUS_FIELD)
    for item in get_done.filter({ID_FIELD: job_id}).run(conn):
        result = item
    return result


@wrap_rethink_errors
@wrap_connection
def get_output_content(job_id, max_size=1024, conn=None):
    """
    returns the content buffer for a job_id if that job output exists

    :param job_id: <str> id for the job
    :param max_size: <int> truncate after [max_size] bytes
    :param conn: (optional)<connection> to run on
    :return: <str> or <bytes>
    """
    content = None
    check_status = RBO.filter({OUTPUTJOB_FIELD: {ID_FIELD: job_id}}).run(conn)
    for status_item in check_status:
        content = _truncate_output_content_if_required(status_item, max_size)
    return content


def _truncate_output_content_if_required(item, max_size):
    if max_size \
            and CONTENT_FIELD in item \
            and len(item[CONTENT_FIELD]) > max_size:
        content = "{}\n[truncated]".format(item[CONTENT_FIELD][:max_size])
    elif CONTENT_FIELD in item:
        content = item[CONTENT_FIELD]
    else:
        content = ""
    return content


@wrap_rethink_errors
@wrap_connection
def plugin_exists(plugin_name, conn=None):
    """

    :param plugin_name:
    :param conn:
    :return: <bool> whether plugin exists
    """
    return plugin_name in RPX.table_list().run(conn)


@wrap_rethink_errors
@wrap_connection
def plugin_list(conn=None):
    """

    :param conn:
    :return: <list> list of all plugins
    """
    return RPX.table_list().run(conn)


@wrap_rethink_generator_errors
@wrap_connection
def get_jobs(plugin_name,
             verify_job=True, conn=None):
    """
    :param plugin_name: <str>
    :param verify_job: <bool>
    :param conn: <connection> or <NoneType>
    :return: <generator> yields <dict>
    """
    job_cur = _jobs_cursor(plugin_name).run(conn)
    for job in job_cur:
        if verify_job and not verify(job, Job()):
            continue #to the next job... warn?
        yield job


@wrap_rethink_errors
@wrap_connection
def get_next_job(plugin_name, location=None, port=None,
                 verify_job=True, conn=None, **kwargs):
    """

    :param plugin_name: <str>
    :param verify_job: <bool>
    :param conn: <connection> or <NoneType>
    :return: <dict> or <NoneType>
    """
    custom_filter = kwargs.get(CUSTOM_FILTER_NAME)
    job_cur = _jobs_cursor(plugin_name,
                           location, port,
                           custom_filter).limit(1).run(conn)
    for job in job_cur:
        if verify_job and not verify(job, Job()):
            continue
        return job
    return None


@wrap_rethink_errors
@wrap_connection
def get_next_job_by_location(plugin_name, loc, verify_job=True, conn=None):
    """
    Deprecated - Use get_next_job
    """
    return get_next_job(plugin_name, loc, verify_job=verify_job, conn=conn)


@wrap_rethink_errors
@wrap_connection
def get_next_job_by_port(plugin_name, port, verify_job=True, conn=None):
    """
    Deprecated - Use get_next_job
    """
    return get_next_job(plugin_name, None, port, verify_job, conn)


@wrap_rethink_errors
@wrap_connection
def get_job_by_id(job_id, conn=None):
    """returns the job with the given id

    :param job_id: <str> id of the job
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> job with the given id
    """
    job = RBJ.get(job_id).run(conn)
    return job


@deprecated_function(replacement="brain.controller.plugins.get_ports_by_ip")
def get_ports_by_ip_controller(ip_address,
                               conn=None):
    from ..controller.plugins import get_ports_by_ip
    return get_ports_by_ip(ip_address, conn=conn)


@deprecated_function(replacement="brain.controller.plugins.get_plugin_by_name")
def get_plugin_by_name_controller(plugin_name,
                                  conn=None):
    from ..controller.plugins import get_plugin_by_name
    return get_plugin_by_name(plugin_name, conn=conn)
