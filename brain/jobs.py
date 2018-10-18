"""
controls Job related changes
"""
from decorator import decorator
from .decorators import verify_jobs_args_is_tuple, verify_jobs_args_length
from .brain_pb2 import Job, Jobs
from .checks import verify
from .static import BEGIN, INVALID, VALID, READY, STOP, PENDING, \
    DONE, ERROR, WAITING, ACTIVE, SUCCESS, FAILURE, TRANSITION, \
    COMMAND_FIELD, INPUT_FIELD, OPTIONAL_FIELD, VALUE_FIELD


class JobsError(Exception):
    """
    Base Jobs exception
    """


class InvalidStateTransition(JobsError):
    """
    Simple exception to identify invalid state transition

    State Transition governed by The Brain Documentation
    """
    pass


class InvalidState(JobsError):
    """
    Simple exception to identify invalid state transition

    State Transition governed by The Brain Documentation
    """
    pass


STATES = {BEGIN: {SUCCESS: READY,
                  FAILURE: ERROR,
                  TRANSITION: frozenset([VALID,
                                         READY,
                                         INVALID,
                                         ERROR,
                                         STOP])},
          INVALID: {SUCCESS: VALID,
                    FAILURE: INVALID,
                    TRANSITION: frozenset([VALID,
                                           INVALID])},
          VALID: {SUCCESS: WAITING,
                  FAILURE: INVALID,
                  TRANSITION: frozenset([WAITING,
                                         INVALID])},
          READY: {SUCCESS: PENDING,
                  FAILURE: ERROR,
                  TRANSITION: frozenset([STOP,
                                         PENDING,
                                         ERROR])},
          PENDING: {SUCCESS: DONE,
                    FAILURE: ERROR,
                    TRANSITION: frozenset([ERROR,
                                           ACTIVE,
                                           DONE])},
          DONE: {SUCCESS: DONE,
                 FAILURE: DONE,
                 TRANSITION: frozenset([DONE])},
          WAITING: {SUCCESS: READY,
                    FAILURE: ERROR,
                    TRANSITION: frozenset([READY,
                                           ERROR,
                                           STOP])},
          ACTIVE: {SUCCESS: DONE,
                   FAILURE: ERROR,
                   TRANSITION: frozenset([ERROR,
                                          DONE])},
          STOP: {SUCCESS: STOP,
                 FAILURE: ERROR,
                 TRANSITION: frozenset([STOP,
                                        ERROR,
                                        WAITING])},
          ERROR: {SUCCESS: DONE,
                  FAILURE: ERROR,
                  TRANSITION: frozenset([DONE,
                                         ERROR])}}


@decorator
def wrap_good_state(func_, *args, **kwargs):
    """
    Decorator/Wrapper to verify the input is an acceptable state
    prior to calling a function on it

    :param f: <function>  to call
    :param args: <tuple> positional args
    :param kwargs: <dict> keyword args
    :return: wrapped function return
    """
    if not verify_state(args[0]):
        raise InvalidState("{} is not a valid state".format(args[0]))
    return func_(*args, **kwargs)


def verify_state(state):
    """
    Verifies a state is acceptable

    :param state: <str> state name
    :return: <bool>
    """
    return state in STATES


@wrap_good_state
def transition_success(state):
    """
    transition to the on-success state

    :param state: <str> state name
    :return: <str> or None
    """
    return STATES[state][SUCCESS]


@wrap_good_state
def transition_fail(state):
    """
    transition to the on-failure state

    :param state: <str> state name
    :return: <str> or None
    """
    return STATES[state][FAILURE]


@wrap_good_state
def transition(prior_state, next_state):
    """
    Transitions to a non-standard state

    Raises InvalidStateTransition if next_state is not allowed.

    :param prior_state: <str>
    :param next_state: <str>
    :return: <str>
    """
    if next_state not in STATES[prior_state][TRANSITION]:
        acceptable = STATES[prior_state][TRANSITION]
        err = "cannot {}->{} may only {}->{}".format(prior_state,
                                                     next_state,
                                                     prior_state,
                                                     acceptable)
        raise InvalidStateTransition(err)
    return next_state


def verify_job(job):
    """
    verifies a job

    :param job: <dict>
    :return: <bool>
    """
    return verify(job, Job())


def verify_jobs(jobs):
    """
    verifies list of jobs

    :param job: <list>
    :return: <bool>
    """
    return verify(jobs, Jobs())


def _get_args_loop(job, key):
    args_tuple = list()
    for job_args in job[COMMAND_FIELD][key]:
        args_tuple.append(job_args[VALUE_FIELD])
    return args_tuple


def get_args(job):
    """
    This function gets the arguments from a job
    :param job: job dictionary
    :return: input tuple, optional tuple
    """
    return tuple(_get_args_loop(job, INPUT_FIELD)), \
        tuple(_get_args_loop(job, OPTIONAL_FIELD))


def _apply_args_loop(job, args, key):
    for i in range(len(args)):
        job[COMMAND_FIELD][key][i][VALUE_FIELD] = args[i]


@verify_jobs_args_length
@verify_jobs_args_is_tuple
def apply_args(job, inputs, optional_inputs=None):
    """
    This function is error checking before the job gets
    updated.
    :param job: Must be a valid job
    :param inputs: Must be a tuple type
    :param optional_inputs: optional for OptionalInputs
    :return: job
    """
    _apply_args_loop(job, inputs, INPUT_FIELD)
    _apply_args_loop(job, optional_inputs, OPTIONAL_FIELD)
    return job
