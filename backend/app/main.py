from fastapi import FastAPI

from core import db_context
from controllers.api import prediction_controller
from controllers.view import view_controller
from services import model_service


db_context.create_tables()
app = FastAPI(redoc_url=None, docs_url="/api/docs")  # api app
view = FastAPI(redoc_url=None, docs_url=None)  # view app


# Mount routers
app.include_router(prediction_controller.router, prefix="/api")
view.include_router(view_controller.router)


# mount panel app to the main api app
app.mount("/api/admin", view)  # Mount the view app under /api/view
