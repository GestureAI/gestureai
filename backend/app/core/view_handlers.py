from fastapi import FastAPI
from fastapi import Request
from fastapi import HTTPException

from services import page_service


def register_not_found_handler(app: FastAPI):
    @app.exception_handler(404)
    async def not_found_handler(req: Request, exc: HTTPException):
        return page_service.show_404_page()
