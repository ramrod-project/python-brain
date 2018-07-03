"""
assortment of wrapped queries
"""
from ..brain_pb2 import Job
from ..checks import verify
from ..connection import rethinkdb as r
from .decorators import wrap_connection
from .decorators import wrap_rethink_generator_errors
from .decorators import wrap_rethink_errors
from . import RPX, RBT, RBJ, RBO, RPC, RPP


def _jobs_cursor(plugin_name):
    return RBJ.filter((r.row["JobTarget"]["PluginName"] == plugin_name) &
                      (r.row["Status"] == "Ready")).order_by('StartTime')


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
    results = targets.filter({"PluginName": plugin_name}).run(conn)
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
    results = RPX.table(plugin_name).run(conn)
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
        {"CommandName": command_name}).run(conn)
    for command in commands:
        continue  # exhausting the cursor
    return command


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
    for item in RBJ.filter({'id': job_id,
                            'Status': "Done"}).run(conn):
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
    check_status = RBO.filter({"OutputJob": {'id': job_id}}).run(conn)
    for status_item in check_status:
        content = _truncate_output_content_if_required(status_item, max_size)
    return content


def _truncate_output_content_if_required(item, max_size):
    if max_size and "Content" in item and len(item['Content']) > max_size:
        content = "{}\n[truncated]".format(item['Content'][:max_size])
    elif "Content" in item:
        content = item['Content']
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


@wrap_rethink_generator_errors
@wrap_connection
def get_jobs(plugin_name,
             verify_job=False, conn=None):
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
def get_next_job(plugin_name,
                 verify_job=False, conn=None):
    """

    :param plugin_name: <str>
    :param verify_job: <bool>
    :param conn: <connection> or <NoneType>
    :return: <dict> or <NoneType>
    """
    job_cur = _jobs_cursor(plugin_name).limit(1).run(conn)
    for job in job_cur:
        if verify_job and not verify(job, Job()):
            continue
        return job
    return None


@wrap_rethink_errors
@wrap_connection
def get_plugin_by_name_controller(plugin_name,
                                  conn=None):
    """

    :param plugin_name: <str> name of plugin
    :param conn: <rethinkdb.DefaultConnection>
    :return: <list> rethinkdb cursor
    """
    result = RPC.filter({
        "Name": plugin_name
    }).run(conn)
    return result


@wrap_rethink_errors
@wrap_connection
def get_ports_by_ip_controller(ip_address,
                               conn=None):
    """

    :param interface_name: <str> name of interface
    :param conn: <rethinkdb.DefaultConnection>
    :return: <list> rethinkdb cursor
    """
    if ip_address == "":
        result = RPP.filter({
            "Address": ip_address
        }).run(conn)
    else:
        result = RPP.filter(
            (r.row["Address"] == ip_address) |
            (r.row["Address"] == "")
        ).run(conn)
    return result
