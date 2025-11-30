import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv 

load_dotenv()


class AudioProcessing():

    def __init__(self):
    
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID")

        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found")
        
        if not voice_id:
            raise ValueError("ELEVENLABS_VOICE_ID not found")
    
        self.client = ElevenLabs(api_key=api_key)

        self.transcription_params = {
            "model_id": "scribe_v1",
            "language_code": "es",
        }

        self.text_to_speech_params = {
            "voice_id": voice_id
        }

    def transcribe_audio(self, audio_data):
        """Transcribe audio to text with elevenlabs"""
        
        if audio_data is None:
            return None        
        
        transcription = self.client.speech_to_text.convert(
            file=audio_data,
            model_id=self.transcription_params["model_id"],
            language_code=self.transcription_params["language_code"],
        )    
        
        return transcription.text

    def text_to_speech(self, text):
        """Convert text to speech with elevenlabs"""
        
        audio = self.client.text_to_dialogue.convert(
            inputs=[
                {
                    "text": text,
                    "voice_id": self.text_to_speech_params["voice_id"],
                }
            ]
        )

        return audio
