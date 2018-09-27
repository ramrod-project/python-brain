"""
module holds static variables thay may be used elsewhere

"""
from . import r


ID_FIELD = "id"
COMMAND_FIELD = "JobCommand"
TARGET_FIELD = "JobTarget"
INPUT_FIELD = "Inputs"
OPTIONAL_FIELD = "OptionalInputs"
VALUE_FIELD = "Value"
STATUS_FIELD = "Status"
START_FIELD = "StartTime"
EXPIRE_FIELD = "ExpireTime"
PORT_FIELD = "Port"
TARGET_OPTIONAL_FIELD = "Optional"
LOCATION_FIELD = "Location"
COMMAND_NAME_KEY = "CommandName"
PLUGIN_NAME_KEY = "PluginName"
OUTPUTJOB_FIELD = "OutputJob"
CONTENT_FIELD = "Content"
RECEIVE_TIME_STAMP = "rt"

BEGIN = ""
INVALID = "Invalid"
VALID = "Valid"
READY = "Ready"
STOP = "Stopped"
PENDING = "Pending"
DONE = "Done"
ERROR = "Error"
WAITING = "Waiting"
ACTIVE = "Active"

SUCCESS = "success"
FAILURE = "failure"
TRANSITION = "transition"


BRAIN_DB = "Brain"
AUDIT_DB = "Audit"
PLUGINDB = "Plugins"
CONTROLLER_DB = "Controller"
JOBS = "Jobs"
TARGETS = "Targets"
OUTPUTS = "Outputs"
FILES = "Files"
LOGS = "Logs"
TARGET = "Target"
PLUGIN = "Plugin"
PLUGINS_TABLE = "Plugins"
PORTS_TABLE = "Ports"

LOGLEVEL_KEY = "LOGLEVEL"
STAGE_KEY = "STAGE"

RDB_UPDATE = "update"
RDB_REPLACE = "replace"

TIMEOUT_ERROR = "Job Timeout"

PROD = "PROD"
QA = "QA"
DEV = "DEV"
TESTING = "TESTING"
STAGES = {PROD: 0,
          QA: 1,
          DEV: 2,
          TESTING: 3}


RBT = r.db(BRAIN_DB).table(TARGETS)
RBJ = r.db(BRAIN_DB).table(JOBS)
RBO = r.db(BRAIN_DB).table(OUTPUTS)
RBF = r.db(BRAIN_DB).table(FILES)
RBL = r.db(BRAIN_DB).table(LOGS)
RPX = r.db(PLUGINDB)
RPC = r.db(CONTROLLER_DB).table(PLUGINS_TABLE)
RPP = r.db(CONTROLLER_DB).table(PORTS_TABLE)
