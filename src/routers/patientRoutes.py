from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession
from src.helpers.deps import get_db, get_current_user
import uuid

from src.models.DatabaseModels import PatientModel, UserModel
from src.schema.Schemas import PatientCreate, PatientUpdate, PatientResponse
from src.exceptions.custom_exception import CustomException
from src.logger.custom_logger import logger


patient_router = APIRouter(
    prefix="/api/v1/patients",
    tags=["patients"]
)


@patient_router.post("patients-info-form", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_info_form_patient(
    patient: PatientCreate,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user)
) -> PatientResponse:
    
    try:
        if not user:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: User not authenticated."
            )
        patient = PatientModel(
            name = patient.name,
            gender = patient.gender,
            age = patient.age,
            email = patient.email,
            phone = patient.phone,
        )
        db.add(patient)
        await db.flush()  # Ensure the patient is added to the session and gets an ID
        await db.commit()
        await db.refresh(patient)  # Refresh to get the latest data from the database

        return PatientResponse(
            organization_id=patient.organization_id,
            name=patient.name,
            gender=patient.gender,
            age=patient.age,
            email=patient.email,
            phone=patient.phone

        )

    except Exception as e:
        logger.error(
            f"Error creating patient info form: {str(e)}"
        )
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the patient info form."
        )

   