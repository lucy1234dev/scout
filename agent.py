from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from cloudinary.uploader import upload as cloudinary_upload
#from cloudinary_config import cloudinary
from db_config import get_connection
import requests
#import psycopg2
import json
import os

router = APIRouter()


HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL_VISION = "YuchengShi/LLaVA-v1.5-7B-Plant-Leaf-Diseases-Detection"
HF_MODEL_TEXT = "google/flan-t5-base"
TIMEOUT = 60



def predict_plant_disease(image_url):
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    payload = {
        "inputs": {
            "image": image_url,
            "text": "what plant disease is this?"
        }
    }

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL_VISION}",
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"Error from HuggingFace vision model: {str(exc)}") from exc



def ask_huggingface_question(question: str):
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    payload = {"inputs": question}

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL_TEXT}",
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"Error from HuggingFace text model: {str(exc)}") from exc



@router.post("/analyse")
async def analyse_plants(image: UploadFile = File(...)):
    try:
        # Upload to Cloudinary
        upload_result = cloudinary_upload(image.file)
        image_url = upload_result["secure_url"]

        # Predict disease using HuggingFace model
        prediction_result = predict_plant_disease(image_url)

        # Save result to PostgreSQL
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO images (image_url, disease_prediction) VALUES (%s, %s)",
            (image_url, json.dumps(prediction_result))
        )
        conn.commit()
        cursor.close()
        conn.close()

        return {"image_url": image_url, "prediction": prediction_result}

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(exc)}") from exc



@router.post("/ask")
async def ask_question(question: str = Form(...)):
    try:
        answer = ask_huggingface_question(question)
        return {"question": question, "answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Question failed: {str(exc)}") from exc
