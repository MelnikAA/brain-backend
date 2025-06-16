from fastapi import APIRouter
from app.api.v1.endpoints import users, predictions, auth, whoami, images, patients

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(whoami.router, prefix="/whoami", tags=["whoami"])
api_router.include_router(images.router, prefix="/images", tags=["images"]) 
api_router.include_router(patients.router, prefix="/patients", tags=["patients"]) 