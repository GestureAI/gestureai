from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response

from core import dependencies
from services import page_service
from services import auth_service
from models import dto


router = APIRouter(tags=["Pages"])


@router.get("/")  # Root endpoint for the view app
async def root(req: Request, is_valid: dependencies.token_dependency):
    return page_service.show_panel_page(req, is_valid)


# pages
@router.get("/login")
async def login(req: Request, is_valid: dependencies.token_dependency):
    return page_service.show_login_page(req, is_valid)


# api
@router.post("/login")
async def login_post(res: Response, data: dto.LoginDTO):
    return auth_service.login(res, data)

@router.get("/logout")
async def logout(res: Response):
    return auth_service.logout(res)
