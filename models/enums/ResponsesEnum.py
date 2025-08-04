from enum import Enum

class ResponsesMessages(Enum):
    SUCCESS = "Success"
    FILE_TYPE_NOT_SUPPORTED = "File type not supported"
    FILE_SIZE_LIMIT_EXCEEDED = "File size limit exceeded"
    UPLOAD_FAILED = "Upload failed"
    UPLOAD_SUCCESS = "Upload success"