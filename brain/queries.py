"""
assortment of wrapped queries
"""
from .brain_pb2 import Job, Jobs, Target, Commands
from .checks import verify
from .connection import rethinkdb as r
from .connection import connect
from decorator import decorator

RBT = r.db("Brain").table("Targets")
RBJ = r.db("Brain").table("Jobs")
RBO = r.db("Brain").table("Outputs")
RPX = r.db("Plugins")

@decorator
def wrap_rethink_errors(f, *args, **kwargs):
    """
    Wraps rethinkdb specific errors as builtin/Brain errors

    :param f: <function> to call
    :param args:  <tuple> positional arguments
    :param kwargs: <dict> keyword arguments
    :return: inherits from the called function
    """
    try:
        return f(*args, **kwargs)
    except (r.errors.ReqlOpFailedError,
            r.errors.ReqlError,
            r.errors.ReqlDriverError) as e:
        raise ValueError(str(e))

@decorator
def wrap_rethink_generator_errors(f, *args, **kwargs):
    """

    :param f:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        for data in f(*args, **kwargs):
            yield data
    except (r.errors.ReqlOpFailedError,
            r.errors.ReqlError,
            r.errors.ReqlDriverError) as e:
        raise ValueError(str(e))


@decorator
def wrap_connection(f, *args, **kwargs):
    """
    conn (connection) must be the last positional argument
    in all wrapped functions

    :param f: <function> to call
    :param args:  <tuple> positional arguments
    :param kwargs: <dict> keyword arguments
    :return:
    """
    if not args[-1]:
        new_args = list(args)
        new_args[-1] = connect()
        args = tuple(new_args)
    return f(*args, **kwargs)

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
        if max_size and "Content" in status_item and len(status_item['Content']) > max_size:
            content = "{}\n[truncated]".format(status_item['Content'][:max_size])
        elif "Content" in status_item:
            content = status_item['Content']
        else:
            content = ""
    return content

@wrap_rethink_errors
@wrap_connection
def insert_new_target(plugin_name, location_num,
                      port_num=0, optional="",
                      verify_target=False, conn=None):
    """
    insert_new_target function gets called when the user's input is validated
    and inserts a new target to Brain.Targets table.
    :param plugin_name: <str> user input plugin name
    :param location_num: <str> user input location number
    :param port_num: <str> user input port number
    :param optional: <str> user input optional
    :return: <dict> rethinkdb insert response value
    """
    target = {"PluginName": str(plugin_name),
              "Location": str(location_num),
              "Port": str(port_num),
              "Optional": {"init": str(optional)}}
    if verify_target and not verify(target, Target()):
        raise ValueError("Invalid Target")
    output = RBT.insert([target]).run(conn)
    return output

@wrap_rethink_errors
@wrap_connection
def insert_jobs(jobs, verify_jobs=True, conn=None):
    """
    insert_jobs function inserts data into Brain.Jobs table

    jobs must be in Job format

    :param jobs: <list> of Jobs
    :return: <dict> rethinkdb insert response value
    """
    assert isinstance(jobs, list)
    if verify_jobs and not verify({"Jobs": jobs}, Jobs()):
        raise ValueError("Invalid Jobs")
    inserted = RBJ.insert(jobs).run(conn)
    return inserted

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
def create_plugin(plugin_name, conn=None):
    """
    Creates a new plugin

    :param plugin_name: <str>
    :param conn:
    :return: <bool> successfully inserted
    """
    if not plugin_exists(plugin_name, conn=conn):
        RPX.table_create(plugin_name,
                         primary_key="CommandName"
                         ).run(conn)
    return True

@wrap_rethink_errors
@wrap_connection
def destroy_plugin(plugin_name, conn=None):
    """
    Creates a new plugin

    :param plugin_name: <str>
    :param conn:
    :return: <bool> successfully inserted
    """
    if plugin_exists(plugin_name, conn=conn):
        RPX.table_drop(plugin_name,
                       ).run(conn)
    return True

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
    success = RPX.table(plugin_name).insert(commands,
                                            conflict="update"
                                           ).run(conn)
    return success

@wrap_rethink_generator_errors
@wrap_connection
def get_next_job(plugin_name,
                 verify_job=False, conn=None):
    """

    :param plugin_name: <str>
    :param verify_job: <bool>
    :param conn: <connection> or <NoneType>
    :return: <generator> yields <dict>
    """
    job_cur = RBJ.filter((r.row["JobTarget"]["PluginName"] == plugin_name) &
                         (r.row["Status"] == "Ready")).run(conn)
    for job in job_cur:
        if verify_job and not verify(job, Job()):
            continue #to the next job... warn?
        yield job
