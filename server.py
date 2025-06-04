from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os
from datetime import datetime
import uuid
import logging
import aiofiles
from leo import Leo, ClinicalInput
from config import Config
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Leo Clinical Documentation Assistant",
    description="AI-powered clinical documentation assistant for hospital in-patient rounds",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Leo with configuration
config = Config()
leo = Leo(config)

# Create upload directories if they don't exist
UPLOAD_DIR = "uploads"
AUDIO_DIR = os.path.join(UPLOAD_DIR, "audio")
IMAGE_DIR = os.path.join(UPLOAD_DIR, "images")

for directory in [UPLOAD_DIR, AUDIO_DIR, IMAGE_DIR]:
    os.makedirs(directory, exist_ok=True)

class NoteRequest(BaseModel):
    transcribed_audio: Optional[str] = None
    extracted_text_from_images: Optional[str] = None
    previous_note: Optional[str] = None
    patient_info: Optional[Dict[str, Any]] = None

@app.post("/generate-note")
async def generate_note(request: NoteRequest):
    """
    Generate a structured progress note from clinical input data
    """
    try:
        input_data = ClinicalInput(
            transcribed_audio=request.transcribed_audio,
            extracted_text_from_images=request.extracted_text_from_images,
            previous_note=request.previous_note,
            patient_info=request.patient_info
        )
        note = leo.process_input(input_data)
        formatted_note = leo.format_note(note)
        return {"note": formatted_note}
    except Exception as e:
        logging.exception("Error in /generate-note")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-audio")
async def upload_audio(
    file: UploadFile = File(...),
    patient_info: str = Form(...)
):
    """
    Upload and process audio file
    """
    try:
        # Save audio file with safe filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_ext = os.path.splitext(file.filename)[1]
        filename = f"{timestamp}_{uuid.uuid4().hex}{safe_ext}"
        file_path = os.path.join(AUDIO_DIR, filename)

        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        # Validate patient_info JSON
        try:
            patient_info_json = json.loads(patient_info)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in patient_info")

        # Transcribe audio using OpenAI Whisper
        import openai
        with open(file_path, "rb") as audio_file:
            print("Transcribing audio file...")
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            transcript = transcript_response
            print("Transcription completed. Transcript:", transcript)

        # Generate note using Leo
        input_data = ClinicalInput(
            transcribed_audio=transcript,
            patient_info=patient_info_json
        )
        note = leo.process_input(input_data)
        formatted_note = leo.format_note(note)

        return {
            "message": "Audio file uploaded, transcribed, and note generated successfully.",
            "filename": filename,
            "patient_info": patient_info_json,
            "transcript": transcript,
            "note": formatted_note
        }
    except Exception as e:
        logging.exception("Error in /upload-audio")
        print('Exception:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    patient_info: str = Form(...)
):
    """
    Upload and process image file
    """
    try:
        # Save image file with safe filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_ext = os.path.splitext(file.filename)[1]
        filename = f"{timestamp}_{uuid.uuid4().hex}{safe_ext}"
        file_path = os.path.join(IMAGE_DIR, filename)

        async with aiofiles.open(file_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        # Validate patient_info JSON
        try:
            patient_info_json = json.loads(patient_info)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in patient_info")

        # TODO: Implement image text extraction
        # For now, return a placeholder
        return {
            "message": "Image file uploaded successfully",
            "filename": filename,
            "patient_info": patient_info_json
        }
    except Exception as e:
        logging.exception("Error in /upload-image")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        return {
            "status": "healthy",
            "version": "1.0.0",
            "llm_provider": getattr(config.llm, "provider", "unknown"),
            "llm_model": getattr(config.llm, "model", "unknown")
        }
    except Exception as e:
        logging.exception("Error in /health")
        raise HTTPException(status_code=500, detail=str(e))
