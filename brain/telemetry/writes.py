"""
functions required to put/update telemetry
"""

from ..queries.decorators import wrap_connection, wrap_rethink_errors
from ..brain_pb2 import Telemetry
from ..checks import verify
from ..static import TARGET_OPTIONAL_FIELD
from ..static import RBT
from . import COMMON_FIELD, SPECIFIC_FIELD


def update_telemetry(conn=None, **kwargs):
    """

    :param conn:
    :param kwargs: Must Include:
                        target_id : <str>
                        specific : <dict>
                        common : <dict>
                        verify_telemetry : <bool>
    :return: <tuple> (specific output, common output)
    """
    target_id = kwargs.get("target_id")
    specific = kwargs.get("specific")
    common = kwargs.get("common")
    verify_telemetry = kwargs.get("verify_telemetry")
    specific_out = update_specific(target_id, specific, conn)
    common_out = update_common(target_id, common, verify_telemetry, conn)
    return specific_out, common_out


@wrap_rethink_errors
@wrap_connection
def update_specific(target_id, specific, conn=None):
    """

    :param target_id:
    :param specific:
    :param conn:
    :return:
    """
    output = {}
    if specific:
        data = {TARGET_OPTIONAL_FIELD: {SPECIFIC_FIELD: specific}}
        output = RBT.get(target_id).update(data).run(conn)
    return output


@wrap_rethink_errors
@wrap_connection
def update_common(target_id, common,
                  verify_telemetry=False, conn=None):
    """

    :param target_id:
    :param common:
    :param verify_telemetry:
    :param conn:
    :return:
    """
    output = {}
    if common:
        if verify_telemetry and not verify(common, Telemetry.common()):
            raise ValueError("Invalid Common Telemetry")
        data = {TARGET_OPTIONAL_FIELD: {COMMON_FIELD: common}}
        output = RBT.get(target_id).update(data).run(conn)
    return output
