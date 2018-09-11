"""
module to assess the current environment variables
default values loaded here
"""
from os import environ
from .static import PROD, TESTING, LOGLEVEL_KEY, STAGE_KEY


#https://en.wikipedia.org/wiki/Syslog#Severity_levels
EMERGENCY = "EMERGENCY"
ALERT = "ALERT"
CRITICAL = "CREITICAL"
ERROR = "ERROR"
WARNING = "WARNING"
NOTICE = "NOTICE"
INFORMATIONAL = "INFORMATIONAL"
DEBUG = "DEBUG"
TEST = "TEST"
LOGLEVELS = {EMERGENCY: 0,
             ALERT: 1,
             CRITICAL: 2,
             ERROR: 3,
             WARNING: 4,
             NOTICE: 5,
             INFORMATIONAL: 6,
             DEBUG: 7,
             TEST: 8}


def check_log_env():
    """
    Special environment variable LOGLEVEL may be one of 9 keys in
    <brain.environment.LOGLEVELS>

    :return: <str> (defaults to 'TEST' / most verbose)
    """
    return environ.get(LOGLEVEL_KEY, TEST)


def check_stage_env():
    """
    Special environment variable STAGE may be one of 4 keys in
    <brain.environment.STAGES>

    :return: <str> ( defaults to 'TESTING' )
    """
    return environ.get(STAGE_KEY, TESTING)


def log_env_gte(desired):
    """
    Boolean check if the current environment LOGLEVEL is
    at least as verbose as a desired LOGLEVEL

    :param desired: <str> one of 9 keys in <brain.environment.stage>
    :return: <bool>
    """
    return LOGLEVELS.get(check_log_env()) >= LOGLEVELS.get(desired, LOGLEVELS[TEST])


def check_prod_env():
    """
    Boolean check if the environemnt is production

    :return: <bool>
    """
    return check_stage_env() == PROD


def check_dev_env():
    """
    Boolean check if the environment is anything other than production

    :return: <bool>
    """
    return not check_prod_env()
