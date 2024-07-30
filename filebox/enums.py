
from enum import Enum


class BlobTypes(Enum):
    """ Supported file types """
    PNG = 'image/png'
    JPG = 'image/jpeg'
    PDF = 'application/pdf'

class FileState(Enum):
    OK = 'success'
    NO = 'rejected'
    FAIL = 'failure'