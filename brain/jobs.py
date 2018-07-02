"""
controls Job related changes
"""
from decorator import decorator
from .brain_pb2 import Job, Jobs
from .queries import insert_jobs, is_job_done, get_next_job
from .checks import verify

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
          VALID: {SUCCESS: READY,
                  FAILURE: INVALID,
                  TRANSITION: frozenset([READY,
                                         WAITING,
                                         INVALID])},
          READY: {SUCCESS: PENDING,
                  FAILURE: ERROR,
                  TRANSITION: frozenset([STOP,
                                         PENDING,
                                         ERROR])},
          PENDING: {SUCCESS: DONE,
                    FAILURE: ERROR,
                    TRANSITION: frozenset([STOP,
                                           ERROR,
                                           ACTIVE,
                                           DONE])},
          DONE: {SUCCESS: DONE,
                 FAILURE: ERROR,
                 TRANSITION: frozenset([DONE,
                                        ERROR])},
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
                                        WAITING,
                                        READY])},
          ERROR: {SUCCESS: DONE,
                  FAILURE: ERROR,
                  TRANSITION: frozenset([DONE,
                                         ERROR,
                                         STOP])}
          }


@decorator
def wrap_good_state(f, *args, **kwargs):
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
    return f(*args, **kwargs)


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
