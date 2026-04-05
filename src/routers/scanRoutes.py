from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.helpers.deps import get_db, get_current_user

from src.models.DatabaseModels import UserModel
from src.schema.Schemas import ScanCreate, ScanDetailResponse
from src.exceptions.custom_exception import CustomException
from src.logger.custom_logger import logger
