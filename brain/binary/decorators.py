"""
decorators fro the binary module
"""
from collections import Counter
from decorator import decorator
from .. import r
from ..queries import RBF
from . import PRIMARY_FIELD, PRIMARY_KEY, TIMESTAMP_FIELD, \
    CHUNK_POSTFIX, CHUNK_ZPAD, \
    CONTENT_FIELD, CONTENTTYPE_FIELD, PART_FIELD, PARTS_FIELD, PARENT_FIELD
# import magic at bottom of file

BINARY = r.binary

MEGA_BYTE = 1048576
MAX_PUT = MEGA_BYTE * 95


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
def wrap_split_big_content(func_, *args, **kwargs):
    """
    chunk the content into smaller binary blobs before inserting

    this function should chunk in such a way that this
    is completely transparent to the user.

    :param func_:
    :param args:
    :param kwargs:
    :return: <dict> RethinkDB dict from insert
    """
    obj_dict = args[0]
    if len(obj_dict[CONTENT_FIELD]) < MAX_PUT:
        obj_dict[PART_FIELD] = False
        return func_(*args, **kwargs)
    else:
        return _perform_chunking(func_, *args, **kwargs)


@decorator
def _only_if_file_not_exist(func_, *args, **kwargs):
    """
    horribly non-atomic

    :param func_:
    :param args:
    :param kwargs:
    :return:
    """
    obj_dict = args[1]
    conn = args[-1]
    try:
        RBF.get(obj_dict[PRIMARY_FIELD]).pluck(PRIMARY_FIELD).run(conn)
        err_str = "Duplicate primary key `Name`: {}".format(obj_dict[PRIMARY_FIELD])
        err_dict = {'errors': 1,
                    'first_error':  err_str}
        return err_dict
    except r.errors.ReqlNonExistenceError:
        return func_(*args, **kwargs)


@_only_if_file_not_exist
def _perform_chunking(func_, *args, **kwargs):
    """
    internal function alled only by
    wrap_split_big_content

    performs the actual chunking.

    :param func_:
    :param args:
    :param kwargs:
    :return: <dict> RethinkDB dict from insert
    """
    obj_dict = args[0]
    start_point = 0
    file_count = 0
    new_dict = {}
    resp_dict = Counter({})
    file_list = []
    while start_point < len(obj_dict[CONTENT_FIELD]):
        file_count += 1
        chunk_fn = CHUNK_POSTFIX.format(obj_dict[PRIMARY_FIELD],
                                        str(file_count).zfill(CHUNK_ZPAD))
        new_dict[PRIMARY_FIELD] = chunk_fn
        file_list.append(new_dict[PRIMARY_FIELD])
        new_dict[CONTENTTYPE_FIELD] = obj_dict[CONTENTTYPE_FIELD]
        new_dict[TIMESTAMP_FIELD] = obj_dict[TIMESTAMP_FIELD]
        end_point = file_count * MAX_PUT
        sliced = obj_dict[CONTENT_FIELD][start_point: end_point]
        new_dict[CONTENT_FIELD] = sliced
        new_dict[PART_FIELD] = True
        new_dict[PARENT_FIELD] = obj_dict[PRIMARY_FIELD]
        start_point = end_point
        new_args = (new_dict, args[1])
        resp_dict += Counter(func_(*new_args, **kwargs))

    obj_dict[CONTENT_FIELD] = b""
    obj_dict[PARTS_FIELD] = file_list
    obj_dict[PART_FIELD] = False
    new_args = (obj_dict, args[1])
    resp_dict += Counter(func_(*new_args, **kwargs))
    return resp_dict


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
    if not args[0].get(CONTENTTYPE_FIELD, None):
        content = args[0].get(CONTENT_FIELD, b"")
        try:
            args[0][CONTENTTYPE_FIELD] = magic.from_buffer(content)
        except magic.MagicException:  # pragma: no cover
            args[0][CONTENTTYPE_FIELD] = MockMagic.DEFAULT_MAGIC
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
    except (r.errors.ReqlDriverCompileError, AttributeError):  # pragma: no cover
        pass  # toss in the object as string
    return func_(*args, **kwargs)


class MockMagic(object):  # pragma: no cover
    """
    class to simulate libmagic  if not available
    """
    DEFAULT_MAGIC = "data"

    class MagicException(Exception):  # pragma: no cover
        """
        exception mapped to libmagic.MagicExeption
        """
        pass

    @staticmethod
    def from_buffer(content=None):  # pragma: no cover
        """
        matches python-magic from_buffer api
        :param content: <iterable>
        :return: always returns DEFAULT_MAGIC
        """
        return MockMagic.DEFAULT_MAGIC


try:
    import magic
except ImportError:  # pragma: no cover
    magic = MockMagic
