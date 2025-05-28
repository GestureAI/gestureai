from fastapi import APIRouter
from fastapi import UploadFile

from models import dto
from services import model_service


router = APIRouter(tags=["Prediction"])


@router.post("/check", response_model=dto.PredictionDTO)
def predict_sign(file: UploadFile):
    return model_service.predict_with_telemetry(file.file.read())
