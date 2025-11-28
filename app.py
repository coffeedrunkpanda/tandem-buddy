import base64
import os
import mimetypes
import gradio as gr
import soundfile as sf
import numpy as np
import librosa

"""
Audio-only chat demo

This creates a `gr.Chatbot` and a single `gr.Audio` recorder/upload control.
When the user records or uploads audio and clicks Send, the app:
 - loads the audio (resampling/normalizing helpers included)
 - produces a placeholder transcription (replace `transcribe()` with a real ASR)
 - appends a single user bubble containing the audio player and the transcription below it
 - appends an assistant response bubble (placeholder)

Notes:
 - Uses data URIs to embed the uploaded audio into the chat bubble so it appears inline.
 - For production or long audio, consider streaming, storing files, or returning the filepath
   instead of embedding large base64 payloads.

Dependencies:
  gradio numpy soundfile librosa

Replace `transcribe()` with your ASR of choice (whisper/faster-whisper, cloud API, etc.).
"""


def guess_mime_type(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "audio/wav"


def file_to_data_uri(path: str) -> str:
    """Read a local file and return a data URI suitable for an <audio> tag."""
    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("ascii")
    mime = guess_mime_type(path)
    return f"data:{mime};base64,{b64}"


def load_audio_for_processing(path: str, target_sr: int = 16000):
    """Load audio from `path`, convert to mono and resample to `target_sr`.
    Returns (np.ndarray, sr).
    """
    data, sr = sf.read(path, dtype="float32")
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    if sr != target_sr:
        data = librosa.resample(data, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
    peak = np.max(np.abs(data)) if data.size else 1.0
    if peak > 0:
        data = data / max(peak, 1e-9)
    return data, sr


def transcribe(path: str) -> str:
    """Placeholder transcription function.

    Replace this with a real ASR (whisper/faster-whisper, cloud API, etc.)
    """
    try:
        data, sr = load_audio_for_processing(path)
        duration = len(data) / sr if sr else 0.0
        # Placeholder: return a helpful debugging summary instead of real transcript
        return f"[simulated transcription — {duration:.2f}s audio]"
    except Exception as e:
        return f"[transcription failure: {e}]"


def process_audio_submit(audio_path, chat_history):
    """Event handler for Send button.

    - `audio_path` is typically a string filepath (Gradio `type='filepath'`).
    - `chat_history` is the current list of (user, assistant) tuples for `gr.Chatbot`.
    """
    if not audio_path:
        return chat_history

    # Support cases where Gradio returns a dict-like object
    if isinstance(audio_path, dict):
        # common keys: 'name', 'file', 'path', 'tmp_path'
        for k in ("name", "file", "path", "tmp_path"):
            if k in audio_path and isinstance(audio_path[k], str):
                audio_path = audio_path[k]
                break

    if not isinstance(audio_path, str) or not os.path.exists(audio_path):
        # Nothing we can do
        return chat_history

    # Create data URI to embed audio inline in the chat bubble.
    try:
        audio_data_uri = file_to_data_uri(audio_path)
    except Exception:
        audio_data_uri = ""

    # Get transcription (placeholder)
    transcription = transcribe(audio_path)

    # Build an HTML user bubble: audio player + transcription text below it
    user_html = (
        f"<div class=\"user-audio-bubble\">"
        f"<audio controls src=\"{audio_data_uri}\"></audio>"
        f"<div class=\"transcription\">{transcription}</div>"
        f"</div>"
    )

    # Generate assistant reply (placeholder). Replace with your generation logic.
    assistant_reply = "[assistant reply generated from audio goes here]"

    # Append a new (user, assistant) pair to the chat history so they appear as
    # two-bubble conversation. The user bubble contains audio + transcription.
    # new_history = list(chat_history or []) + [(user_html, assistant_reply)]

    # Data incompatible with messages format. Each message should be a dictionary with 'role' and 'content' keys or a ChatMessage object.

    new_history = list(chat_history or []) + [
    {"role": "user", "content": transcription},
    {"role": "assistant", "content": assistant_reply}
]
    
    return new_history


def clear_chat():
    return []


css_blob = """
.user-audio-bubble { display: block; }
.user-audio-bubble .transcription { margin-top: 6px; color: #333; font-style: italic; }
"""


def main():
    with gr.Blocks() as demo:
        gr.Markdown("## Audio-only Chat — record or upload and click Send")

        chatbot = gr.Chatbot([], type="messages" , elem_id="chatbot", label="Conversation")

        with gr.Row():
            audio_input = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Record or upload audio")
            send_btn = gr.Button("Send")
            clear_btn = gr.Button("Clear")

        send_btn.click(fn=process_audio_submit, inputs=[audio_input, chatbot], outputs=[chatbot])
        clear_btn.click(fn=clear_chat, inputs=None, outputs=[chatbot])

    demo.launch()


if __name__ == "__main__":
    main()
