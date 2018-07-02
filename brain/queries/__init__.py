"""
Query module is getting big
"""

from ..connection import rethinkdb as r
# recursive imports at bottom of file


RBT = r.db("Brain").table("Targets")
RBJ = r.db("Brain").table("Jobs")
RBO = r.db("Brain").table("Outputs")
RBF = r.db("Brain").table("Files")
RPX = r.db("Plugins")

# backward compatible api
from .reads import *
from .writes import *
