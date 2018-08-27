"""
Provides a very thin wrapper to rethinkdb as well as common helper functions
"""
import rethinkdb, rethinkdb as r  # rethinkdb passthrough don't delete

from .connection import connect
from .environment import check_log_env, check_prod_env, check_dev_env, log_env_gte, check_stage_env

from . import binary
from . import controller
from . import queries


