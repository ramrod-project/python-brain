"""
Query module is getting big
"""

# import here for backward compatible
from ..static import RBT, RBJ, RBO, RBF, RPX, RPC, RPP

CUSTOM_FILTER_NAME = "custom_filter"

# backward compatible api
from .reads import *
from .writes import *
