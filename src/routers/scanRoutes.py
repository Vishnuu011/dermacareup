from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.helpers.deps import get_db, get_current_user

from src.models.DatabaseModels import ScanModel, UserModel
from src.schema.Schemas import ScanCreate, ScanDetailResponse
from src.exceptions.custom_exception import CustomException
from src.logger.custom_logger import logger

scan_router = APIRouter(
    prefix="/api/v1/scans",
    tags=["scans"]
)

@scan_router.post("/upload-scan", response_model=ScanDetailResponse, status_code=status.HTTP_201_CREATED)
async def upload_scan_detection(
    scan: ScanCreate,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user)
) -> ScanDetailResponse:
    
    pass