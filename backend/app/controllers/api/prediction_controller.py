from fastapi import APIRouter
from fastapi import UploadFile

from models import dto
from services import fake_service


router = APIRouter(tags=["Prediction"])


@router.post("/check", response_model=dto.PredictionDTO)
def predict_sign(file: UploadFile):
    return fake_service.fake_response()
