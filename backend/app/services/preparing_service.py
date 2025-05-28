# type: ignore
import io
from typing import Any

from PIL import Image
from PIL import ImageOps
from PIL import ImageFile
import mediapipe as mp
import numpy as np


IMAGE_SIZE_PX = 224
EXTRA_PADDING = 30


# clip hand from image
def search_hand(file: bytes) -> Any | None:
    hand_image = None

    with mp.solutions.hands.Hands(
        min_detection_confidence=0.5, static_image_mode=True, max_num_hands=1
    ) as hands:
        img = Image.open(io.BytesIO(file)).convert("RGB")

        # define image sizes
        w, h = img.size

        # search hands
        results = hands.process(np.array(img))
        if results.multi_hand_landmarks is None:
            return hand_image

        for landmarks in results.multi_hand_landmarks:
            # get hand coordinates
            x_list = [int(landmark.x * w) for landmark in landmarks.landmark]
            y_list = [int(landmark.y * h) for landmark in landmarks.landmark]
            x_min, x_max = min(x_list), max(x_list)
            y_min, y_max = min(y_list), max(y_list)

            # Add padding for image with hand
            padding = EXTRA_PADDING
            x_min, y_min = max(0, x_min - padding), max(0, y_min - padding)
            x_max, y_max = min(w, x_max + padding), min(h, y_max + padding)

            # cut hand from imgage
            hand_data = img.crop((x_min, y_min, x_max, y_max))
            hand_image = hand_data
            break

    return hand_image


# resize image and convert to grayscale
def prepare_image(file: ImageFile) -> ImageFile:
    img = file.resize((IMAGE_SIZE_PX, IMAGE_SIZE_PX))
    return ImageOps.grayscale(img)
