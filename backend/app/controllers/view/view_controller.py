from fastapi import APIRouter
from fastapi.responses import PlainTextResponse


router = APIRouter(tags=["Pages"])


@router.get("/")  # Root endpoint for the view app
def root():
    return PlainTextResponse("Welcome to the Panel App!")
