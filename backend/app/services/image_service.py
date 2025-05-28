from io import BytesIO

from fastapi import UploadFile
from magic import from_buffer


_VALID_TYPES = [
    "image/jpeg",
    "image/png",
]


def _get_mime(content: bytes) -> str:
    mime = ""

    file_obj = BytesIO(content)
    # read first 2048 bytes to determine the file type
    mime_type = from_buffer(file_obj.read(2048), True)

    if mime_type:
        mime = mime_type

    return mime


def _is_image(content: bytes) -> bool:
    mime = _get_mime(content)

    return mime in _VALID_TYPES


def validate(file: UploadFile) -> bool:
    """
    Validate the uploaded file to ensure it is an image.
    """
    if not file or not file.file:
        return False

    content = file.file.read()
    if not content:
        return False

    return _is_image(content)
