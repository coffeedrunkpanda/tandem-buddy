import os
import gradio as gr

from .audio_processing import AudioProcessing
from .language_partner import LanguagePartner

empty_transcription_message = "## 📝 Transcriptions\n\nNo messages yet."

class ChatController():
    def __init__(self):
        self.audio_processor = AudioProcessing()
        self.language_partner = LanguagePartner()

        self._message_turn_counter = 1

        if os.path.isdir("temp_data") is False:
            os.makedirs("temp_data")

        self.temp_dir = "temp_data"

        self._history = []

        # Transcriptions list (Actual data storage)
        self._transcriptions = []

        # UI State flags
        self.show_transcriptions = False 
            
    def _process_user_audio_message(self, audio):
        """Process user audio: save audio, get transcription and add to chat"""

        if audio is None:
            return None
        
        # save user audio in temp file
        filename = f"{self.temp_dir}/user_audio_{self._message_turn_counter}.mp3"
        self.audio_processor.save_audio_to_file(audio_data=audio,
                                                filename=filename)

        # obtain answer from language partner
        transcription = self.audio_processor.speech_to_text(audio)
    
        # Add identifier to the message
        self._history.append({
        "role": "user",
        "content": f"🎤 User Audio Message #{self._message_turn_counter}"
        })

        self._history.append({
            "role": "user",
            "content": {
                "path": filename,
            }
        })
        
        # Store transcription
        self._transcriptions.append({
            "role": "user",
            "text": transcription,
            "index": self._message_turn_counter
        })
        
    def _generate_bot_audio_response(self):
        # Get user's last transcription
        user_transcription = self._transcriptions[-1]["text"]
        
        # Generate assistant response text
        assistant_response_text = self.language_partner.get_response(user_transcription)

        # Generate assistant response text
        audio_response = self.audio_processor.text_to_speech(assistant_response_text)
        
        # save assistant audio in temp file
        filename = f"{self.temp_dir}/assistant_audio_{self._message_turn_counter}.mp3"
        self.audio_processor.save_audio_to_file(audio_data=audio_response,
                                                            filename=filename)

        # Add identifier to the message
        self._history.append({
        "role": "assistant",
        "content": f"🤖 Assistant Audio Message #{self._message_turn_counter}"
        })

        self._history.append({
            "role": "assistant",
            "content": {
                "path": filename,
            }
        })
        
        # Store assistant transcription
        self._transcriptions.append({
            "role": "assistant",
            "text": assistant_response_text,
            "index": self._message_turn_counter
        })
        
    def process_conversation_turn(self, audio):
        """Process a full conversation turn: user audio and bot response audio"""

        # Process user audio message
        self._process_user_audio_message(audio)
        self._generate_bot_audio_response()

        # Generate response audio
        self._message_turn_counter += 1

    def clear_all(self):
        self._history = []
        self._transcriptions = []
        self.language_partner.reset_conversation()

        # Clear temp files
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        
        self._message_turn_counter = 1

        # Return empty list for Chatbot, empty string for transcriptions, and empty string for feedback
        return [], empty_transcription_message, ""

    def _format_transcriptions(self):
        """Format transcriptions for display"""
        
        if not self.show_transcriptions or not self._transcriptions:
            return ""
        
        formatted = "## 📝 Transcriptions\n\n"
        
        for i, trans in enumerate(self._transcriptions):
            role_emoji = "🎤" if trans["role"] == "user" else "🤖"
            role_name = "User" if trans["role"] == "user" else "Assistant"
            idx = trans.get('index', i + 1)
            formatted += f"**{role_emoji} {role_name} Audio Message #{idx}**\n\n"
            formatted += f"{trans['text']}\n\n"
            formatted += "---\n\n"
        
        return formatted

    def toggle_transcriptions(self):
        # Toggle transcription panel visibility
        
        self.show_transcriptions = not self.show_transcriptions

        button_text = "Hide Transcriptions" if self.show_transcriptions else "Show Transcriptions"
        
        transcription_text = self._format_transcriptions()
        if not transcription_text and self.show_transcriptions:
            transcription_text = empty_transcription_message
        
        return (
            gr.update(visible=self.show_transcriptions),
            button_text,
            transcription_text
        )

    def generate_feedback(self):
        """Generate feedback for the conversation based on transcriptions"""
        if not self._transcriptions:
            return "## ⚠️ No conversation to analyze yet."
        
        feedback = "## 📊 Final Conversation Feedback\n\n"
        feedback += f"**Total Interactions:** {self._message_turn_counter} turns\n\n"    
        feedback+=self.language_partner.get_detailed_feedback()
        
        return feedback

    def handle_audio_submit(self, audio_filepath):
        # Handle audio submission
        if audio_filepath is None:
            return self._history, self._format_transcriptions(), audio_filepath
        
        with open(audio_filepath, "rb") as f:
            audio = f.read()
            self.process_conversation_turn(audio)

        # Update transcription display
        transcription_display = self._format_transcriptions()

        if not transcription_display and self.show_transcriptions:
            transcription_display = empty_transcription_message
        
        # Return History (for chatbot), Transcription (for panel), and None (to clear audio input)
        return self._history, transcription_display, None
