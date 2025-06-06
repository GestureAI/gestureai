from datetime import datetime
from datetime import timezone

from fastapi.requests import Request
from fastapi import HTTPException
from fastapi.responses import Response
from fastapi.responses import RedirectResponse

from core import jwt_context
from models import dto

from utils.config import CONFIG


def login(res: Response, data: dto.LoginDTO):
    if data.password != CONFIG.PANEL_PASSWORD:
        raise HTTPException(status_code=401, detail="Wrong password")

    exp_date = datetime.now(timezone.utc) + CONFIG.SESSION_TIME
    json_token = jwt_context.encode({}, exp_date)

    res.set_cookie(key=CONFIG.COOKIES_KEY_NAME, value=json_token, expires=CONFIG.SESSION_TIME.seconds)


def logout(res: Response):
    res = RedirectResponse("/api/admin/login")
    res.delete_cookie(key=CONFIG.COOKIES_KEY_NAME)
    return res


def validate_token(req: Request) -> bool:
    token = req.cookies.get(CONFIG.COOKIES_KEY_NAME)
    if not token:
        return False

    try:
        data = jwt_context.decode(token)
        return data is not None

    except Exception as e:
        print(f"Token validation failed: {e}")
        return False
