from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from cloudinary.uploader import upload as cloudinary_upload
from db_config import get_connection
import requests
import json
import os

router = APIRouter()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"
TIMEOUT = 60


def predict_plant_disease(image_url):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": "You are a plant disease expert."},
        {"role": "user", "content": f"What plant disease is shown in this image? {image_url}"}
    ]

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.2
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"Error from Groq vision model: {str(exc)}") from exc


def ask_groq_question(question: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"Error from Groq text model: {str(exc)}") from exc


@router.post("/analyse")
async def analyse_plants(image: UploadFile = File(...)):
    try:
        upload_result = cloudinary_upload(image.file)
        image_url = upload_result["secure_url"]

        prediction_result = predict_plant_disease(image_url)

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
        answer = ask_groq_question(question)
        return {"question": question, "answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Question failed: {str(exc)}") from exc
