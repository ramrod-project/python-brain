"""
decorator objects for other functions in the main brain module
"""

from decorator import decorator


COMMAND_FIELD = "JobCommand"
INPUT_FIELD = "Inputs"
OPTIONAL_FIELD = "OptionalInputs"
VALUE_FIELD = "Value"


@decorator
def verify_jobs_args_length(func_, *args, **kwargs):
    """

    :param job:
    :param inputs:
    :param optional_inputs:
    :return:
    """
    job = args[0]
    inputs = args[1]
    optional_inputs = args[2]
    assert len(job[COMMAND_FIELD][INPUT_FIELD]) == len(inputs)
    if not optional_inputs:
        optional_inputs = tuple()
    assert len(job[COMMAND_FIELD][OPTIONAL_FIELD]) == len(optional_inputs)
    return func_(*args, **kwargs)


@decorator
def verify_jobs_args_is_tuple(func_, *args, **kwargs):
    """

    :param func_:
    :param args:
    :param kwargs:
    :return:
    """
    inputs = args[1]
    optional_inputs = args[2]
    if not isinstance(inputs, tuple) or not isinstance(optional_inputs, tuple):
        raise ValueError('Input must be a tuple')
    return func_(*args, **kwargs)
