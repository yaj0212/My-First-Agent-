import os
import uuid
import gradio as gr
from agent import chat

OUTPUT_DIR = os.path.abspath("output")


def respond(message, history, thread_id):
    thread_id = (thread_id or "").strip() or "default"
    try:
        response = chat(message, thread_id=thread_id)
    except Exception as e:
        response = f"Error: {e}"
    return response


def new_session():
    return [], str(uuid.uuid4())[:8]


with gr.Blocks(title="My First Agent") as demo:
    gr.Markdown(
        f"# My First Agent\n"
        f"Chat with your agent. It can show code directly in the chat **and** save files to:\n\n"
        f"`{OUTPUT_DIR}`"
    )

    with gr.Row():
        thread_input = gr.Textbox(
            value="default",
            label="Session ID",
            info="Each unique ID is an isolated conversation thread.",
            scale=4,
        )
        new_btn = gr.Button("New Session", scale=1, variant="secondary")

    chatbot = gr.Chatbot(label="Chatbot", height=480)

    chat_ui = gr.ChatInterface(
        fn=respond,
        chatbot=chatbot,
        additional_inputs=[thread_input],
        examples=[
            ["Write a Python script that prints the Fibonacci sequence"],
            ["Generate a CSV with columns Name, Age, City and 3 sample rows"],
            ["Create a Markdown file with a project README template"],
            ["Generate a PDF with a short introduction about AI agents"],
            ["Create an Excel file tracking monthly expenses with 5 rows"],
            ["Write a Word document with a simple cover letter template"],
            ["Create a Jupyter notebook with two cells: one that imports pandas, one that prints Hello World"],
        ],
    )

    new_btn.click(fn=new_session, outputs=[chatbot, thread_input])

if __name__ == "__main__":
    demo.launch()
