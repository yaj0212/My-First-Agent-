import gradio as gr
from agent import chat

def respond(message, history, thread_id):
    if not thread_id.strip():
        thread_id = "default"
    try:
        response = chat(message, thread_id=thread_id)
    except Exception as e:
        response = f"Error: {e}"
    return response


with gr.Blocks(title="My First Agent") as demo:
    gr.Markdown("# My First Agent\nAsk me to generate **CSV, Markdown, Python, PDF, Excel, Word, or Jupyter** files.")

    thread_input = gr.Textbox(
        value="default",
        label="Session ID",
        info="Change this to start a fresh conversation thread.",
        scale=1,
    )

    chat_ui = gr.ChatInterface(
        fn=respond,
        additional_inputs=[thread_input],
        examples=[
            ["Generate a CSV with columns Name, Age, City and 3 sample rows"],
            ["Write a Python script that prints the Fibonacci sequence"],
            ["Create a Markdown file with a project README template"],
            ["Generate a PDF with a short introduction about AI agents"],
            ["Create an Excel file tracking monthly expenses with 5 rows"],
            ["Write a Word document with a simple cover letter template"],
            ["Create a Jupyter notebook with two cells: one that imports pandas, one that prints Hello World"],
        ],
        type="messages",
    )

if __name__ == "__main__":
    demo.launch()
