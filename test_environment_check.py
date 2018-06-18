
from os import environ
from .brain.environment import check_log_env, check_stage_env, check_dev_env, check_prod_env, log_env_gte

def test_default_loglevel():
    if "LOGLEVEL" in environ:
        del(environ['LOGLEVEL'])
    assert check_log_env() == "TEST"
    assert not check_prod_env()
    assert check_dev_env()

def test_emergency_loglevel():
    environ['LOGLEVEL'] = "EMERGENCY"
    assert log_env_gte("EMERGENCY")
    assert not log_env_gte("TEST")
    assert not check_prod_env()
    assert check_dev_env()
    del (environ['LOGLEVEL'])

def test_warning_loglevel():
    environ['LOGLEVEL'] = "WARNING"
    assert log_env_gte("WARNING")
    assert not log_env_gte("TEST")
    assert not check_prod_env()
    assert check_dev_env()
    del (environ['LOGLEVEL'])

def test_debug_loglevel():
    environ['LOGLEVEL'] = "DEBUG"
    assert log_env_gte("WARNING")
    assert log_env_gte("DEBUG")
    assert not log_env_gte("TEST")
    assert not check_prod_env()
    assert check_dev_env()
    del (environ['LOGLEVEL'])

def test_test_loglevel():
    environ['LOGLEVEL'] = "TEST"
    assert log_env_gte("WARNING")
    assert log_env_gte("DEBUG")
    assert log_env_gte("TEST")
    assert not check_prod_env()
    assert check_dev_env()
    del (environ['LOGLEVEL'])

def test_stage_env():
    old_stage = environ.get("STAGE", "")
    if "STAGE" in environ:
        del(environ['STAGE'])
    assert check_stage_env() == "TESTING"
    assert not check_prod_env()
    assert check_dev_env()
    environ['STAGE'] = old_stage

def test_dev_env():
    old_stage = environ.get("STAGE", "")
    if "STAGE" in environ:
        del (environ['STAGE'])
    assert check_dev_env()
    assert not check_prod_env()
    environ['STAGE'] = old_stage


def test_not_dev_env():
    old_stage = environ.get("STAGE", "")
    if "STAGE" in environ:
        del (environ['STAGE'])
    assert not check_prod_env()
    assert check_dev_env()
    environ['STAGE'] = old_stage

def test_set_bad_stage():
    old_stage = environ.get("STAGE", "")
    environ['STAGE'] = "PRODUCTION"
    assert not check_prod_env()
    assert check_dev_env()
    environ['STAGE'] = old_stage

def test_set_dev_check_stage():
    old_stage = environ.get("STAGE", "")
    environ['STAGE'] = "DEV"
    assert check_dev_env()
    assert not check_prod_env()
    environ['STAGE'] = old_stage

def test_set_prod__check_stage():
    old_stage = environ.get("STAGE", "")
    environ['STAGE'] = "PROD"
    assert not check_dev_env()
    assert check_prod_env()
    environ['STAGE'] = old_stage
