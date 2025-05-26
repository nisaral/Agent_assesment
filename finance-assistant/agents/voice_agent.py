from fastapi import FastAPI
from pydantic import BaseModel
import whisper
from gtts import gTTS
import os

app = FastAPI()
model = whisper.load_model("base")

class VoiceRequest(BaseModel):
    audio_file: str
    text: str = None

@app.post("/stt")
async def speech_to_text(request: VoiceRequest):
    result = model.transcribe(request.audio_file)
    return {"text": result["text"]}

@app.post("/tts")
async def text_to_speech(request: VoiceRequest):
    output_file = "output.mp3"
    tts = gTTS(request.text)
    tts.save(output_file)
    return {"audio_file": output_file}