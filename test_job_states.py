
from pytest import raises
from .brain.jobs import verify_state, transition_success, transition_fail, \
    transition, InvalidStateTransition, InvalidState, JobsError
from .brain.jobs import STATES, SUCCESS, FAILURE, TRANSITION, BEGIN, READY, ERROR

INVALID_STATE = "INVALID SATE"

def test_states_verify():
    for state in STATES:
        assert verify_state(state)

def test_bad_state():
    assert not verify_state(INVALID_STATE)


def test_states_have_success():
    for state in STATES:
        next_state = transition_success(state)
        assert next_state is None or isinstance(next_state, str)

def test_states_have_success_verify():
    for state in STATES:
        next_state = transition_success(state)
        if next_state:
            assert verify_state(next_state)

def test_states_have_fail():
    for state in STATES:
        next_state = transition_fail(state)
        assert next_state is None or isinstance(next_state, str)

def test_states_have_fail_verify():
    for state in STATES:
        next_state = transition_fail(state)
        if next_state:
            assert verify_state(next_state)

def test_states_acceptable_movements():
    for state in STATES:
        for next_state in STATES[state][TRANSITION]:
            assert verify_state(next_state)
            assert transition(state, next_state)

def test_states_unacceptable_movements():
    for state in STATES:
        with raises(InvalidStateTransition):
            transition(state, INVALID_STATE)

def test_next_state_from_bad_state():
    with raises(InvalidState):
        transition_success(INVALID_STATE)

def test_error_state_from_bad_state():
    with raises(InvalidState):
        transition_fail(INVALID_STATE)


def test_next_state_from_bad_state_broad_error():
    with raises(JobsError):
        transition_success("INVALID_STATE")

def test_error_state_from_bad_state_broad_error():
    with raises(JobsError):
        transition_fail("Invalid_state")

def test_begin_state_SUCCESS():
    assert transition_success(BEGIN) == READY

def test_begin_state_Error():
    assert transition_fail(BEGIN) == ERROR

def test_all_state_transitions():
    for from_state in STATES:
        for to_state in STATES:
            allowed = to_state in STATES[from_state][TRANSITION]
            if allowed:
                assert transition(from_state, to_state)
            else:
                with raises(InvalidStateTransition):
                    transition(from_state, to_state)

def test_succes_fail_in_allowed():
    for state in STATES:
        if STATES[state][SUCCESS]:
            assert STATES[state][SUCCESS] in STATES[state][TRANSITION]
        if STATES[state][FAILURE]:
            assert STATES[state][FAILURE] in STATES[state][TRANSITION]