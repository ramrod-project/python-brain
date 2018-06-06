from os import environ

#https://en.wikipedia.org/wiki/Syslog#Severity_levels
LOGLEVELS = {"EMERGENCY": 0,
             "ALERT": 1,
             "CRITICAL": 2,
             "ERROR": 3,
             "WARNING": 4,
             "NOTICE": 5,
             "INFORMATIONAL": 6,
             "DEBUG": 7,
             "TEST": 8}

STAGES = {"PROD": 0,
          "QA": 1,
          "DEV": 2,
          "TESTING": 3}

def check_log_env():
    """
    Special environment variable LOGLEVEL may be one of 9 keys in
    <brain.environment.LOGLEVELS>

    :return: <str> (defaults to 'TEST' / most verbose)
    """
    return environ.get("LOGLEVEL", "TEST")

def check_stage_env():
    """
    Special environment variable STAGE may be one of 4 keys in
    <brain.environment.STAGES>

    :return: <str> ( defaults to 'TESTING' )
    """
    return environ.get("STAGE", "TESTING")

def log_env_gte(desired):
    """
    Boolean check if the current environment LOGLEVEL is
    at least as verbose as a desired LOGLEVEL

    :param desired: <str> one of 9 keys in <brain.enviornment.stage>
    :return: <bool>
    """
    return LOGLEVELS.get(check_log_env()) >= LOGLEVELS.get(desired, LOGLEVELS['TEST'])

def check_prod_env():
    """
    Boolean check if the environemnt is production

    :return: <bool>
    """
    return check_stage_env() == "PROD"

def check_dev_env():
    """
    Boolean check if the environment is anything other than production

    :return: <bool>
    """
    return not check_prod_env()
