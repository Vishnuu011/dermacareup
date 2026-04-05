import cloudinary
from src.config.config import settings
import cloudinary.uploader
import os
from src.exceptions.custom_exception import CloudinaryUploadException
from src.logger.custom_logger import logger


cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET
)

def upload_image_to_cloudinary(image_path: str):
    try:
        response = cloudinary.uploader.upload(image_path)
        return response['secure_url']
    except Exception as e:
        logger.error(f"Error uploading image to Cloudinary: {e}")
        raise CloudinaryUploadException(
            message="Failed to upload image to Cloudinary",
            detail=str(e)
        )