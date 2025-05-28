from os.path import exists
import time

from fastapi import HTTPException
import keras
import numpy as np

from services import image_service
from services import preparing_service
from services import telemetry_service
from factories import prediciton_factory
from utils.config import CONFIG
from models import dto


_MODEL_PATH = f"./tf_models/{CONFIG.TF_MODEL_NAME}"
_ANSWERS = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    " ",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]

# show error if model file is not found
if not exists(_MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {_MODEL_PATH}")

MODEL: keras.models.Sequential = keras.saving.load_model(_MODEL_PATH)  # type: ignore


def predict_with_telemetry(image_bytes: bytes) -> dto.PredictionDTO:
    start_time = time.perf_counter()
    prediction = predict(image_bytes)
    duration = time.perf_counter() - start_time

    # register telemetry
    duration_ms = int(duration * 1000)  # convert to milliseconds
    telemetry_service.register(prediction.char, prediction.precision, duration_ms)

    return prediction


def predict(image_bytes: bytes) -> dto.PredictionDTO:
    # validate image
    if image_service.validate(image_bytes) is False:
        raise HTTPException(422, "Image type is not supported")

    # search hand image to predict
    hand = preparing_service.search_hand(image_bytes)
    if hand is None:
        return prediciton_factory.create("", 0.0)

    # make prediction
    prepared_image = preparing_service.prepare_image(hand)
    return _send_to_model(prepared_image)


def _send_to_model(image) -> dto.PredictionDTO:
    img_array = np.array(image)
    img_array = np.expand_dims(img_array, axis=0)

    # make prediction
    prediction = MODEL.predict(img_array, verbose="0")

    # convert to dto
    result = int(np.argmax(prediction))
    char_prediction = _ANSWERS[result]
    precision = prediction[0][result]

    return prediciton_factory.create(char_prediction, float(precision), 0.2)
