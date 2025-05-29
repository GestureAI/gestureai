from contextlib import asynccontextmanager

from fastapi import FastAPI
import logging

from services import model_service


_IMAGE_PATH = "./tf_models/cold_boot.png"
_LOGGER = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if _LOGGER.isEnabledFor(logging.INFO):
        _LOGGER.info("Start model loading into memory ...")

    # load image
    with open(_IMAGE_PATH, "rb") as file:
        image_bytes = file.read()

    # make first prediction to load the model into memory
    model_service.predict(image_bytes)

    if _LOGGER.isEnabledFor(logging.INFO):
        _LOGGER.info("Model loaded successfully.")

    yield
    # before stop
