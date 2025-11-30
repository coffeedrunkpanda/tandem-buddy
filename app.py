import wave
import tempfile

import numpy as np
import gradio as gr

from audio_processing import AudioProcessing
from language_partner import LanguagePartner


# TODO: fix message counter for user and assistant messages
# Custom CSS for layout
css = """
.transcription-panel {
    border-left: 2px solid #e0e0e0;
    padding-left: 20px;
    max-height: 600px;
    overflow-y: auto;
}
.main-chat {
    padding-right: 20px;
}
"""

empty_transcription_message = "## 📝 Transcriptions\n\nNo messages yet."


# TODO: Fix functions below and add to audio_processing.py
def save_audio_to_file(audio):
    """Save audio numpy array to a temporary WAV file"""
    if audio is None:
        return None
    
    sample_rate, audio_data = audio
    
    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    
    # Normalize audio data to int16
    if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
        audio_data = (audio_data * 32767).astype(np.int16)
    
    # Write WAV file
    with wave.open(temp_file.name, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    return temp_file.name

def generate_audio_response(text):
    """Generate audio response from text"""
    # Create a simple sine wave as placeholder
    sample_rate = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = (np.sin(2 * np.pi * 440 * t) * 0.3 * 32767).astype(np.int16)
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    
    with wave.open(temp_file.name, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    return temp_file.name

def generate_response_text(user_transcription):
    """Generate text response"""
    return f"Assistant: I heard you say '{user_transcription}'. Here's my response!"

def process_audio_message(audio, history, transcriptions):
    """Process user audio: save and add to chat"""
    if audio is None:
        return history, None, transcriptions
    
    # Save audio to file
    audio_file = save_audio_to_file(audio)
    
    # Transcribe user audio
    transcription = transcribe_audio(audio)
    
    # Add user message with audio
    history = history or []
    message_index = len(history)

    # Add identifier to the message
    history.append({
    "role": "user",
    "content": f"🎤 User Audio Message #{message_index + 1}"
    })

    history.append({
        "role": "user",
        "content": {
            "path": audio_file,
        }
    })
    


    # Store transcription
    transcriptions = transcriptions or []
    transcriptions.append({
        "role": "user",
        "text": transcription,
        "index": message_index
    })
    
    return history, None, transcriptions

def generate_response(history, transcriptions):
    """Generate bot audio response"""
    if not history or not transcriptions:
        return history, transcriptions
    
    # Get user's last transcription
    user_transcription = transcriptions[-1]["text"]
    
    # Generate response text
    response_text = generate_response_text(user_transcription)
    
    # Generate audio response
    response_audio_file = generate_audio_response(response_text)
    
    message_index = len(history)
    
    # Add identifier to the message
    history.append({
    "role": "assistant",
    "content": f"🤖 Assistant Audio Message #{message_index + 1}"
    })

    history.append({
        "role": "assistant",
        "content": {
            "path": response_audio_file,
        }
    })
    
    # Store assistant transcription
    transcriptions.append({
        "role": "assistant",
        "text": response_text,
        "index": message_index
    })
    
    return history, transcriptions

def format_transcriptions(transcriptions, show_transcriptions):
    """Format transcriptions for display"""
    if not show_transcriptions or not transcriptions:
        return ""
    
    formatted = "## 📝 Transcriptions\n\n"
    for i, trans in enumerate(transcriptions):
        role_emoji = "🎤" if trans["role"] == "user" else "🤖"
        role_name = "User" if trans["role"] == "user" else "Assistant"
        formatted += f"**{role_emoji} {role_name} Audio Message #{trans['index'] + 1}**\n\n"
        formatted += f"{trans['text']}\n\n"
        formatted += "---\n\n"
    
    return formatted


with gr.Blocks(css=css) as demo:
    gr.Markdown("# 🎙️ Audio Chat with Transcriptions Panel")
    
    # Store transcriptions in state
    transcriptions_state = gr.State([])
    show_transcriptions_state = gr.State(False)
    
    with gr.Row():
        # Main chat area
        with gr.Column(scale=2, elem_classes="main-chat") as chat_col:
            chatbot = gr.Chatbot(
                label="Conversation",
                type="messages",
                height=500
            )

            # TODO: investigate using type="filepath" for audio input
            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone", "upload"],
                    type="numpy",
                    label="Record or Upload Audio"
                )
            
            with gr.Row():
                send_btn = gr.Button("Send Audio", variant="primary", scale=1)
                clear_btn = gr.Button("Clear Chat", scale=1)
                transcribe_toggle = gr.Button("Show Transcriptions", scale=1)
                # TODO: Add "Feedback" button later
        
        # Transcription panel (initially hidden)
        with gr.Column(scale=1, visible=False, elem_classes="transcription-panel") as transcription_col:
            transcription_display = gr.Markdown(
                value=empty_transcription_message,
                label="Transcriptions"
            )

    # Toggle transcription panel visibility
    def toggle_transcriptions(show_state, transcriptions):
        new_state = not show_state
        button_text = "Hide Transcriptions" if new_state else "Show Transcriptions"
        transcription_text = format_transcriptions(transcriptions, new_state)
        if not transcription_text:
            transcription_text = empty_transcription_message
        
        return (
            new_state,
            gr.update(visible=new_state),
            button_text,
            transcription_text
        )

    transcribe_toggle.click(
        toggle_transcriptions,
        inputs=[show_transcriptions_state, transcriptions_state],
        outputs=[show_transcriptions_state, transcription_col, transcribe_toggle, transcription_display]
    )

    # Handle audio submission
    def handle_audio_submit(audio, history, transcriptions, show_state):
        if audio is None:
            return history, None, transcriptions, format_transcriptions(transcriptions, show_state)
        
        # Add user audio
        history, _, transcriptions = process_audio_message(audio, history, transcriptions)
        # Generate bot response
        history, transcriptions = generate_response(history, transcriptions)
        
        # Update transcription display
        transcription_text = format_transcriptions(transcriptions, show_state)
        if not transcription_text:
            transcription_text = empty_transcription_message
        
        return history, None, transcriptions, transcription_text

    send_btn.click(
        handle_audio_submit,
        inputs=[audio_input, chatbot, transcriptions_state, show_transcriptions_state],
        outputs=[chatbot, audio_input, transcriptions_state, transcription_display]
    )

    # Removed auto-submit on recording stop

    # Clear chat
    def clear_all():
        return [], None, [], empty_transcription_message

    clear_btn.click(
        clear_all,
        outputs=[chatbot, audio_input, transcriptions_state, transcription_display]
    )



if __name__ == "__main__":
    demo.launch()
