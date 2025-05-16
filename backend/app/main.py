from fastapi import FastAPI
from fastapi import UploadFile

from models import dto
from services import fake_service


app = FastAPI()


@app.post("/check", response_model=dto.PredictionDTO)
def predict_sign(file: UploadFile):
    return fake_service.fake_response()
