# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2019

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging

from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel

class File_(BaseModel):
    """
    A File as written in the database
    """
    archived: bool
    created_by: str
    filelength: int
    locale: str
    mimetype: str
    name: str
    path: str
    topic: str
    topicdate: str     # YYYY-MM-DD
    url: str
    _id: str
    _version: int
    _documenttype: str
    _creationtime: datetime
    _modificationtime: datetime

class FileOptional(BaseModel):
    """
    A File as written in the database
    """
    archived: Optional[bool]
    created_by: Optional[str]
    filelength: Optional[int]
    id: Optional[str]
    locale: Optional[str]
    mimetype: Optional[str]
    name: Optional[str]
    path: Optional[str]
    topic: Optional[str]
    topicdate: Optional[str]     # YYYY-MM-DD
    url: Optional[str]
    _id: Optional[str]
    _version: Optional[int]
    _documenttype: Optional[str]
    _creationtime: Optional[datetime]
    _modificationtime: Optional[datetime]

class FileIn(BaseModel):
    """
    contains the minimal fields (doctype and name) to create a new page
    """
    content: bytes           # base64 encoded content of file
    name: str
    topic: str

class FileOut(BaseModel):
    """
    A readonly view used for listing files
    """
    archived: bool = False
    created_by: str = 'webmaster'
    filelength: int
    id: str
    locale: str = ''
    mimetype: str
    name: str
    topic: str = 'Unknown'    # report BM, report GA, ....
    topicdate: str
    url: str
    _creationtime: datetime
    _modificationtime: datetime

class FileUpdate(BaseModel):
    """
    An update to a file: all fields are optional
    """
    archived: Optional[bool] = None
    created_by: Optional[str] = None
    content: Optional[bytes] = None
    locale: Optional[str] = None
    name: Optional[str] = None
    topic: Optional[str] = None
    topicdate: str

file_fields = {
    FileOut: FileOut.__fields__.keys(),
    FileOptional: FileOptional.__fields__.keys(),
}

class FileListOut(BaseModel):
    files: List[Any]

