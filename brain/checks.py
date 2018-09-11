"""
functions to perform checks used by other areas of the brain

functions should all return a boolean if possible.
"""

from google.protobuf.message import EncodeError
import dict_to_protobuf #this lib allows extra keys
from .static import TARGET_OPTIONAL_FIELD, ERROR, TARGET, PLUGIN
dict_to_protobuf.l.setLevel(ERROR.upper())


def verify(value, msg):
    """
    C-style validator

    Keyword arguments:
    value -- dictionary to validate (required)
    msg -- the protobuf schema to validate against (required)

    Returns:
        True: If valid input
        False: If invalid input
    """
    return bool(value) and \
           converts_to_proto(value, msg) and \
           successfuly_encodes(msg) and \
           special_typechecking(value, msg)


def special_typechecking(value, msg):
    """
    Special Typechecking not available via protocol itself
    :param value: <dict>
    :param msg: <proto object>
    :return: <bool>
    """
    result = True
    if msg.DESCRIPTOR.name == TARGET:
        result &= special_target_typecheck(value)
    elif msg.DESCRIPTOR.name == PLUGIN:
        result &= special_plugin_checking(value)
    return result


def special_plugin_checking(value):
    """

    :param value:
    :return:
    """
    return verify_plugin_contents(value)


def special_target_typecheck(value):
    """
    Special type checking for the target object
    :param value: <dict>
    :return: <bool>
    """
    result = True
    # if key:Optional exists, it must be a dict object
    result &= isinstance(value.get(TARGET_OPTIONAL_FIELD, dict()), dict)
    return result


def converts_to_proto(value, msg, raise_err=False):
    """
    Boolean response if a dictionary can convert into the proto's schema

    :param value: <dict>
    :param msg: <proto object>
    :param raise_err: <bool> (default false) raise for troubleshooting
    :return: <bool> whether the dict can covert
    """
    result = True
    try:
        dict_to_protobuf.dict_to_protobuf(value, msg)
    except TypeError as type_error:
        if raise_err:
            raise type_error
        result = False
    return result


def successfuly_encodes(msg, raise_err=False):
    """
    boolean response if a message contains correct information to serialize

    :param msg: <proto object>
    :param raise_err: <bool>
    :return: <bool>
    """
    result = True
    try:
        msg.SerializeToString()
    except EncodeError as encode_error:
        if raise_err:
            raise encode_error
        result = False
    return result


def strip(value, msg):
    """
    Strips all non-essential keys from the value dictionary
    given the message format protobuf

    raises ValueError exception if value does not have all required keys

    :param value: <dict> with arbitrary keys
    :param msg: <protobuf> with a defined schema
    :return: NEW <dict> with keys defined by msg, omits any other key
    """
    dict_to_protobuf.dict_to_protobuf(value, msg)
    try:
        msg.SerializeToString()  #raise error for insufficient input
    except EncodeError as encode_error:
        raise ValueError(str(encode_error))
    output = dict_to_protobuf.protobuf_to_dict(msg)
    return output

from .controller.plugins import verify_plugin_contents