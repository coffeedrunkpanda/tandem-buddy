import os
import types
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv 

from .utils import running_from_docker_container

# TODO: add transcription params to the .env file

class AudioProcessing():

    def __init__(self) -> None:
    
        print("Initializing AudioProcessing with ElevenLabs API...")
        print("Running from Docker container:", running_from_docker_container())
        
        if not running_from_docker_container():
            load_dotenv()
            api_key = os.getenv("ELEVENLABS_API_KEY")
            voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        else:
            api_key = os.environ.get("ELEVENLABS_API_KEY")
            voice_id = os.environ.get("ELEVENLABS_VOICE_ID") 


        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found")
        
        if not voice_id:
            raise ValueError("ELEVENLABS_VOICE_ID not found")
    
        self._client = ElevenLabs(api_key=api_key)

        self._transcription_params = {
            "model_id": "scribe_v1",
            "language_code": "es",
        }

        self._text_to_speech_params = {
            "voice_id": voice_id
        }

    def speech_to_text(self, audio_data)-> str:
        """Transcribe audio to text with elevenlabs"""
        
        if audio_data is None:
            return None        
        
        transcription = self._client.speech_to_text.convert(
            file=audio_data,
            model_id=self._transcription_params["model_id"],
            language_code=self._transcription_params["language_code"],
        )    
        
        return transcription.text

    def text_to_speech(self, text):
        """Convert text to speech with elevenlabs"""
        
        audio = self._client.text_to_dialogue.convert(
            inputs=[
                {
                    "text": text,
                    "voice_id": self._text_to_speech_params["voice_id"],
                }
            ]
        )

        return audio

    def save_audio_to_file(self, audio_data, filename) -> None:
        if audio_data is None:
            return None

        if isinstance(audio_data, types.GeneratorType):  
            with open(filename, "wb") as out_file:
                for chunk in audio_data:
                    out_file.write(chunk)

        elif isinstance(audio_data, bytes):
            with open(filename, "wb") as out_file:
                out_file.write(audio_data)

if __name__ == "__main__":
    audio_processor = AudioProcessing()
    
    # Example usage speech to text
    audio_file_path = "teste.m4a"

    with open(audio_file_path, "rb") as f:
        audio_data = f.read()
        print(type(audio_data))
        transcription_text = audio_processor.speech_to_text(audio_data)
        print("Transcription:", transcription_text)

 
    # Example usage text to speech
    text = "Hola, ¿cómo estás, amiga? Espero que tengas un gran día, guapa."
    audio_response = audio_processor.text_to_speech(text)
    print(type(audio_response))

    # Example saving audio response to file
    audio_processor.save_audio_to_file(audio_response, "temp/audio_response_x.mp3")
