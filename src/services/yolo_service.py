import os, sys
from pathlib import Path
from ultralytics import YOLO
from src.logger.custom_logger import logger
from src.exceptions.custom_exception import CustomException
import cv2
import uuid
from typing import Tuple, List, Dict


model_path = Path(__file__).parent.parent.parent / "best_model" / "best.pt"

model = YOLO(model_path)

async def detect_objects(image_path: str) -> Tuple[List[Dict], str]:

    try:
        results = model(image_path)
        detections = []

        annoted_path = f"annotated_{uuid.uuid4()}.jpg"

        image = cv2.imread(image_path)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                desease = model.names[class_id]
                detections.append({
                    "disease_name": desease,
                    "confidence_score": confidence,
                    "severity" : "High" if confidence > 0.8 else "Medium" if confidence > 0.5 else "Low",
                    "bounding_box": f"{x1}, {y1}, {x2}, {y2}"
                })
                cv2.rectangle(
                    image, (x1, y1), (x2, y2), (0, 255, 0), 2
                )
                cv2.putText(
                    image, f"{desease} {confidence:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )
        cv2.imwrite(annoted_path, image)
        return detections, annoted_path
    except Exception as e:
        logger.error(
            f"Error in detect_objects: {str(e)}"
        )
        raise CustomException(
            status_code=500,
            detail="An error occurred while processing the image."
        )
