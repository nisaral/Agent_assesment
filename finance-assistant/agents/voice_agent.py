from pydantic import BaseModel
from gtts import gTTS
import os
import whisper
import tempfile
import base64
import logging
from .base_agent import create_base_app

app = create_base_app("Voice Agent")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize whisper model
try:
    model = whisper.load_model("base")
    logger.info("Successfully initialized Whisper model")
except Exception as e:
    logger.error(f"Failed to initialize Whisper model: {e}")
    model = None

class TTSRequest(BaseModel):
    text: str

class STTRequest(BaseModel):
    audio: str

@app.post("/tts")
async def tts(request: TTSRequest):
    try:
        if not request.text:
            return {"error": "No text provided"}
            
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            try:
                # Generate audio
                tts = gTTS(text=request.text, lang='en')
                tts.save(tmp.name)
                
                # Read and encode audio
                with open(tmp.name, "rb") as f:
                    audio_data = base64.b64encode(f.read()).decode()
                    
                return {"audio_file": audio_data}
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp.name)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {e}")
                    
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return {"error": f"Failed to convert text to speech: {str(e)}"}

@app.post("/stt")
async def stt(request: STTRequest):
    try:
        if not model:
            return {"error": "Speech recognition model not initialized"}
            
        if not request.audio:
            return {"error": "No audio data provided"}
            
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            try:
                # Decode and save audio data
                audio_data = base64.b64decode(request.audio.split(",")[1])
                tmp.write(audio_data)
                tmp.flush()
                
                # Transcribe audio
                result = model.transcribe(tmp.name)
                
                if not result or "text" not in result:
                    return {"error": "Failed to transcribe audio"}
                    
                return {"text": result["text"].strip()}
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp.name)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {e}")
                    
    except Exception as e:
        logger.error(f"STT error: {str(e)}")
        return {"error": f"Failed to convert speech to text: {str(e)}"}
@app.post("/run")
async def run(request: VoiceRequest):
    return await process_voice(request)