"""
assortment of wrapped queries
"""
from ..brain_pb2 import Jobs, Target, Commands
from ..checks import verify
from ..jobs import WAITING, STATES, transition_success
from ..connection import rethinkdb as r
from ..decorators import deprecated_function
from .decorators import wrap_connection, wrap_rethink_errors
from .decorators import START_FIELD, STATUS_FIELD
from . import RPX, RBT, RBJ, RPC, RPP, RBO
from .reads import plugin_exists, get_job_by_id

VALID_STATES = STATES


def waiting_filter(lte_time):
    """
    generates a filter for status==waiting and
    time older than lte_time

    :param lte_time: <float> time()
    :return:
    """
    return ((r.row[STATUS_FIELD] == WAITING) &
            (r.row[START_FIELD] <= lte_time))


@deprecated_function(replacement="brain.controller.plugins.has_port_conflict")
def _check_port_conflict(port_data,
                         existing):
    from ..controller.plugins import has_port_conflict
    return has_port_conflict(port_data, existing)


@wrap_rethink_errors
@wrap_connection
def insert_target(target, verify_target=False,
                  conn=None):
    """

    :param target:  <dict> of Target() format
    :param verify_target: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb insert response value
    """
    if verify_target and not verify(target, Target()):
        raise ValueError("Invalid Target")
    return RBT.insert([target]).run(conn)


@wrap_rethink_errors
@wrap_connection
def insert_jobs(jobs, verify_jobs=True, conn=None):
    """
    insert_jobs function inserts data into Brain.Jobs table

    jobs must be in Job format

    :param jobs: <list> of Jobs
    :param verify_jobs: <bool>
    :param conn: <rethinkdb.DefaultConnection>
    :return: <dict> rethinkdb insert response value
    """
    assert isinstance(jobs, list)
    if verify_jobs and not verify({"Jobs": jobs}, Jobs()):
        raise ValueError("Invalid Jobs")
    inserted = RBJ.insert(jobs).run(conn)
    return inserted


@wrap_rethink_errors
@wrap_connection
def update_job_status(job_id, status, conn=None):
    """Updates a job to a new status

    :param job_id: <str> the id of the job
    :param status: <str> new status
    :param conn: <connection> a database connection (default: {None})

    :return: <dict> the update dicts for the job and the output
    """
    if status not in VALID_STATES:
        raise ValueError("Invalid status")
    job_update = RBJ.get(job_id).update({STATUS_FIELD: status}).run(conn)
    if job_update["replaced"] == 0 and job_update["unchanged"] == 0:
        raise ValueError("Unknown job_id: {}".format(job_id))
    id_filter = (r.row["OutputJob"]["id"] == job_id)
    output_job_status = {"OutputJob": {"Status": status}}
    output_update = RBO.filter(id_filter).update(output_job_status).run(conn)
    return {str(RBJ): job_update, str(RBO): output_update}


@wrap_rethink_errors
@wrap_connection
def write_output(job_id, content, conn=None):
    """writes output to the output table

    :param job_id: <str> id of the job
    :param content: <str> output to write
    :param conn:
    """
    output_job = get_job_by_id(job_id, conn)
    results = {}
    if output_job is not None:
        entry = {
            "OutputJob": output_job,
            "Content": content
        }
        results = RBO.insert(entry, conflict="replace").run(conn)
    return results


@wrap_rethink_errors
@wrap_connection
def create_plugin(plugin_name, conn=None):
    """
    Creates a new plugin

    :param plugin_name: <str>
    :param conn:
    :return: <dict> rethinkdb response
    """
    results = {}
    if not plugin_exists(plugin_name, conn=conn):
        results = RPX.table_create(plugin_name,
                                   primary_key="CommandName").run(conn)
    return results


@wrap_rethink_errors
@wrap_connection
def destroy_plugin(plugin_name, conn=None):
    """
    Creates a new plugin

    :param plugin_name: <str>
    :param conn:
    :return: <dict> rethinkdb response
    """
    results = {}
    if plugin_exists(plugin_name, conn=conn):
        results = RPX.table_drop(plugin_name).run(conn)
    return results


@wrap_rethink_errors
@wrap_connection
def advertise_plugin_commands(plugin_name, commands,
                              verify_commands=False,
                              conn=None):
    """

    :param plugin_name:
    :param commands:
    :param verify_commands:
    :param conn:
    :return:
    """
    assert isinstance(commands, list)
    if verify_commands and not verify({"Commands": commands},
                                      Commands()):
        raise ValueError("Invalid Commands")
    plugin = RPX.table(plugin_name)
    success = plugin.insert(commands,
                            conflict="update").run(conn)
    return success


@deprecated_function(replacement="brain.controller.plugins.create_plugin")
def create_plugin_controller(plugin_data,
                             verify_commands=False,
                             conn=None):
    from ..controller.plugins import create_plugin
    return create_plugin(plugin_data,
                         verify_commands=verify_commands,
                         conn=conn)


@deprecated_function(replacement="brain.controller.plugins.create_port")
def create_port_controller(port_data,
                           verify_port=False,
                           conn=None):
    from ..controller.plugins import create_port
    return create_port(port_data,
                       verify_port=verify_port,
                       conn=conn)


@deprecated_function(replacement="brain.controller.plugins.update_plugin")
def update_plugin_controller(plugin_data,
                             verify_plugin=False,
                             conn=None):
    from ..controller.plugins import update_plugin
    return update_plugin(plugin_data,
                         verify_plugin=verify_plugin,
                         conn=conn)


@wrap_rethink_errors
@wrap_connection
def transition_waiting(start_time, conn=None):
    """

    :param start_time: <float> from time.time()
    :return: <dict>
    :raises may raise reqlerror, wrapped into ValueError by decorator
    """
    wait_filter = waiting_filter(start_time)
    status_change = {STATUS_FIELD: transition_success(WAITING)}
    return RBJ.filter(wait_filter).update(status_change).run(conn)
