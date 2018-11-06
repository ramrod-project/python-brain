"""
Helpers to move binary files in and out of Brain.Files
"""
PRIMARY_FIELD = "Name"
PRIMARY_KEY = "id"
CONTENT_FIELD = "Content"
CONTENTTYPE_FIELD = "ContentType"
TIMESTAMP_FIELD = "Timestamp"
PARTS_FIELD = "Parts"
PART_FIELD = "Part"
PARENT_FIELD = "Parent"

CHUNK_POSTFIX = "{}.{}"
CHUNK_ZPAD = 3

from .data import *
