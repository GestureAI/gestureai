from fastapi import APIRouter
from fastapi.requests import Request
from core.jinja_context import templates


router = APIRouter(tags=["Pages"])


@router.get("/")  # Root endpoint for the view app
async def root(req: Request):
    return templates.TemplateResponse(req, "test.jinja", {"key": "Some value"})
