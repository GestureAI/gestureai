from typing import Annotated

from fastapi import Depends

from services import auth_service


token_dependency = Annotated[bool, Depends(auth_service.validate_token)]
