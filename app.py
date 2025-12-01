import gradio as gr
from tandem_buddy.chat_controller import ChatController, empty_transcription_message

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
.feedback-section {
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
}
"""

header_md = "# 🎙️ Tandem Buddy"

with gr.Blocks(css=css) as demo:
    gr.Markdown(header_md)
    
    integrated_chat = ChatController()
    
    with gr.Row():
        # Main chat area
        with gr.Column(scale=2, elem_classes="main-chat") as chat_col:
            chatbot = gr.Chatbot(
                label="Conversation",
                type="messages",
                height=500
            )

            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone", "upload"],
                    type="filepath",
                    label="Record or Upload Audio"
                )
            
            with gr.Row():
                send_btn = gr.Button("Send Audio", variant="primary", scale=1)
                clear_btn = gr.Button("Clear Chat", scale=1)
                transcribe_toggle = gr.Button("Show Transcriptions", scale=1)
                feedback_btn = gr.Button("Get Final Feedback", variant="secondary", scale=1)
            
            # Feedback Section
            with gr.Row(visible=True) as feedback_row:
                feedback_display = gr.Markdown(elem_classes="feedback-section")
        
        # Transcription panel (initially hidden)
        with gr.Column(scale=1, visible=False, elem_classes="transcription-panel") as transcription_col:
            transcription_display = gr.Markdown(
                value=empty_transcription_message,
                label="Transcriptions"
            )

    # Event Listeners
    transcribe_toggle.click(
        integrated_chat.toggle_transcriptions,
        inputs=[],
        outputs=[transcription_col, transcribe_toggle, transcription_display]
    )

    # Handle audio submission
    send_btn.click(
        integrated_chat.handle_audio_submit,
        inputs=[audio_input],
        outputs=[chatbot, transcription_display, audio_input]
    )

    # Feedback Button
    feedback_btn.click(
        integrated_chat.generate_feedback,
        inputs=[],
        outputs=[feedback_display]
    )

    # Clear everything including feedback
    clear_btn.click(
        integrated_chat.clear_all,
        outputs=[chatbot, transcription_display, feedback_display]
    )


if __name__ == "__main__":
    # demo.launch()

    demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False
    )