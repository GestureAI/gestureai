from fastapi import FastAPI

from core import db_context
from core import view_handlers
from core.lifespan import lifespan
from controllers.api import prediction_controller
from controllers.view import view_controller


db_context.create_tables()
app = FastAPI(redoc_url=None, docs_url="/api/docs", lifespan=lifespan)  # api app
view = FastAPI(redoc_url=None, docs_url=None)  # view app

# Mount routers
app.include_router(prediction_controller.router, prefix="/api")
view.include_router(view_controller.router)

# Register handlers
view_handlers.register_not_found_handler(view)  # Register 404 handler for the view app

# mount panel app to the main api app
app.mount("/api/admin", view)  # Mount the view app under /api/view
