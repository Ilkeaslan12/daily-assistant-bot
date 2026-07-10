import re
import io
import os
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

def text_to_voice(text: str, filename: str = "response.ogg") -> str:
    """Cleans text and converts it to speech."""
    # Remove markdown characters for better TTS processing
    clean_text = re.sub(r'[*_`#\-]', '', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Generate speech
    tts = gTTS(text=clean_text, lang='en', slow=False)
    tts.save(filename)
    return filename

def voice_to_text(ogg_file_path: str) -> str:
    """Converts audio file to text using Google Speech Recognition."""
    try:
        audio = AudioSegment.from_file(ogg_file_path, format="ogg")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="en-US")
            return text
            
    except sr.UnknownValueError:
        return "ERROR: SPEECH_UNRECOGNIZED"
    except sr.RequestError:
        return "ERROR: STT_SERVICE_UNAVAILABLE"
    except Exception as e:
        print(f"STT Conversion Error: {e}")
        return None