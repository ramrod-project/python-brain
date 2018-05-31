"""
assortment of wrapped queries
"""
from .brain_pb2 import Jobs, Target
from .checks import verify
from .connection import rethinkdb as r
from .connection import connect

RBT = r.db("Brain").table("Targets")
RBJ = r.db("Brain").table("Jobs")
RBO = r.db("Brain").table("Output")
RPX = r.db("Plugins")

def get_targets(conn=None):
    """
    get_brain_targets function from Brain.Targets table.

    :return: <generator> yields dict objects
    """
    conn = conn if conn else connect()
    targets = RBT
    results = targets.run(conn)
    for item in results:
        yield item

def get_targets_by_plugin(plugin_name, conn=None):
    """
    get_targets_by_plugin function from Brain.Targets table

    :return: <generator> yields dict objects
    """
    conn = conn if conn else connect()
    targets = RBT
    results = targets.run(conn).filter({"PluginName":plugin_name})
    for item in results:
        yield item

def get_plugin_commands(plugin_name, conn=None):
    """
    get_specific_commands function queries Plugins.<PluginName> table
    the plugin name will be based off the user selection from the ui.
    It will return the query onto w2 as a dictionary nested in a list.

    :param plugin_name: <str> user's plugin selection
    :return: <generator> yields dictionaries
    """
    conn = conn if conn else connect()
    results = RPX.table(plugin_name).run(conn)
    for item in results:
        yield item

def get_plugin_command(plugin_name, command_name, conn=None):
    """
    get_specific_command function queries a specific CommandName

    :param plugin_name: <str> PluginName
    :param command_name: <str> CommandName
    :return: <dict>
    """
    conn = conn if conn else connect()
    commands = RPX.table(plugin_name).filter(
        {"CommandName": command_name}).run(conn)
    for command in commands:
        continue  # exhausting the cursor
    return command

def is_job_done(job_id, conn=None):
    """
    is_job_done function checks to if Brain.Jobs Status is 'Done'

    :param job_id: <str> id for the job
    :param conn: (optional)<connection> to run on
    :return: <dict> if job is done <false> if
    """
    conn = conn if conn else connect()
    result = False
    for item in RBJ.filter({'id': job_id,
                            'Status': "Done"}).run(conn):
        result = item
    return result

def get_output_content(job_id, max_size=1024, conn=None):
    """
    returns the content buffer for a job_id if that job output exists

    :param job_id: <str> id for the job
    :param max_size: <int> truncate after [max_size] bytes
    :param conn: (optional)<connection> to run on
    :return: <str> or <bytes>
    """
    conn = conn if conn else connect()
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



    return query_specific_plugin_name
def insert_new_target(plugin_name, location_num,
                      port_num=0, optional="",
                      verify_target=True, conn=None):
    """
    insert_new_target function gets called when the user's input is validated
    and inserts a new target to Brain.Targets table.
    :param plugin_name: <str> user input plugin name
    :param location_num: <str> user input location number
    :param port_num: <str> user input port number
    :param optional: <str> user input optional
    :return: <dict> rethinkdb insert response value
    """
    conn = conn if conn else connect()
    target = {"PluginName": str(plugin_name),
              "Location": str(location_num),
              "Port": str(port_num),
              "Optional": {"init": str(optional)}}
    if verify_target and not verify(target, Target()):
        raise ValueError("Invalid Target")
    output = RBT.insert([target]).run(conn)
    return output


def insert_jobs(jobs, verify_jobs=True, conn=None):
    """
    insert_jobs function inserts data into Brain.Jobs table

    jobs must be in Job format

    :param jobs: <list> of Jobs
    :return: <dict> rethinkdb insert response value
    """
    conn = conn if conn else connect()
    assert isinstance(jobs, list)
    if verify_jobs and not verify({"Jobs": jobs}, Jobs()):
        raise ValueError("Invalid Jobs")
    inserted = RBJ.insert(jobs).run(conn)
    return inserted
