"""
Query module is getting big
"""

# import here for backward compatible
from ..static import RBT, RBJ, RBO, RBF, RPX, RPC, RPP

CUSTOM_FILTER_NAME = "custom_filter"
IDX_OUTPUT_JOB_ID = "Output_job_id"
IDX_STATUS = "Status"

# backward compatible api
from .reads import *
from .writes import *
