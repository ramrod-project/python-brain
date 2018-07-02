"""
decorators fro the binary module
"""

import magic
from decorator import decorator
from .. import r

BINARY = r.binary
PRIMARY_FIELD = "Name"
PRIMARY_KEY = "id"
CONTENT_FIELD = "Content"
CONTENTTYPE_FIELD = "ContentType"


@decorator
def wrap_name_to_id(func_, *args, **kwargs):
    """
    destination (rethinkdb) needs the id field as primary key
    put the Name field into the ID field
    :param func_:
    :param args:
    :param kwargs:
    :return:
    """
    assert isinstance(args[0], dict)
    args[0][PRIMARY_KEY] = args[0].get(PRIMARY_FIELD, "")
    return func_(*args, **kwargs)

@decorator
def wrap_guess_content_type(func_, *args, **kwargs):
    """
    guesses the content type with libmagic if available
    :param func_:
    :param args:
    :param kwargs:
    :return:
    """
    assert isinstance(args[0], dict)
    if not args[0].get(CONTENTTYPE_FIELD, None) and magic:
        content = args[0].get(CONTENT_FIELD, b"")
        try:
            args[0][CONTENTTYPE_FIELD] = magic.from_buffer(content)
        except magic.MagicException:  # pragma: no cover
            args[0][CONTENTTYPE_FIELD] = "data"
    return func_(*args, **kwargs)


@decorator
def wrap_content_as_binary_if_needed(func_, *args, **kwargs):
    """
    destination (rethinkdb) needs the id field as primary key
    put the Name field into the ID field
    :param func_:
    :param args:
    :param kwargs:
    :return:
    """
    assert isinstance(args[0], dict)
    try:
        args[0][CONTENT_FIELD] = BINARY(args[0].get(CONTENT_FIELD, b""))
    except AttributeError:  # pragma: no cover
        pass  # toss in the object as string
    return func_(*args, **kwargs)
