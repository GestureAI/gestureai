from fastapi import APIRouter
from fastapi.requests import Request

from services import page_service


router = APIRouter(tags=["Pages"])


@router.get("/")  # Root endpoint for the view app
async def root(req: Request):
    return page_service.show_test_page(req)
