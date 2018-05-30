

from google.protobuf.message import EncodeError
import dict_to_protobuf #this lib allows extra keys
dict_to_protobuf.l.setLevel("ERROR")

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
    result = True
    dict_to_protobuf.dict_to_protobuf(value, msg)
    try:
        msg.SerializeToString()
    except EncodeError:
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
