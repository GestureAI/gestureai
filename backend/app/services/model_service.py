from os.path import exists

import keras

from utils.config import CONFIG


_MODEL_PATH = f"./tf_models/{CONFIG.TF_MODEL_NAME}"

# show error if model file is not found
if not exists(_MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {_MODEL_PATH}")

MODEL: keras.models.Sequential = keras.saving.load_model(_MODEL_PATH)  # type: ignore
