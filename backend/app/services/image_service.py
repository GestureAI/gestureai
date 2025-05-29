from io import BytesIO

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


def validate(content: bytes) -> bool:
    mime = _get_mime(content)
    return mime in _VALID_TYPES
