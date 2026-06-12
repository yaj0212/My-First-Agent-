import os
import re
import uuid
import tempfile
import gradio as gr
from agent import chat

TEMP_DIR = os.path.join(tempfile.gettempdir(), "my-first-agent")
os.makedirs(TEMP_DIR, exist_ok=True)

FILE_SAVED_RE = re.compile(r"FILE_SAVED:(\S+)")

EXAMPLES = [
    "Write a Python script that prints the Fibonacci sequence",
    "Generate a CSV with columns Name, Age, City and 3 sample rows",
    "Create a Markdown README template for a Python project",
    "Generate a PDF intro about AI agents",
    "Create an Excel file tracking monthly expenses with 5 rows",
    "Write a Word document with a simple cover letter template",
    "Create a Jupyter notebook that imports pandas and prints Hello World",
]


def extract_files(text: str):
    return FILE_SAVED_RE.findall(text)


def clean_response(text: str) -> str:
    return FILE_SAVED_RE.sub("", text).strip()


def respond(message, history, thread_id, known_files):
    thread_id = (thread_id or "").strip() or "default"
    if not message or not message.strip():
        return history, known_files, known_files
    try:
        raw = chat(message, thread_id=thread_id)
    except Exception as e:
        raw = f"Error: {e}"

    new_paths = extract_files(raw)
    response = clean_response(raw)

    if new_paths:
        names = [os.path.basename(p) for p in new_paths]
        response += f"\n\n**File ready to download:** {', '.join(names)}  \nClick the filename in the Downloads panel below."

    updated_files = known_files + [p for p in new_paths if os.path.exists(p)]
    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response},
    ]
    return history, updated_files, updated_files


def new_session(known_files):
    return [], str(uuid.uuid4())[:8], known_files


def fill_example(example_text):
    return example_text


with gr.Blocks(title="My First Agent") as demo:
    gr.Markdown("# My First Agent\nChat with your agent. Files are generated in chat first — download them when you're ready.")

    file_state = gr.State([])

    with gr.Row():
        thread_input = gr.Textbox(
            value="default",
            label="Session ID",
            info="Each unique ID is an isolated conversation thread.",
            scale=4,
        )
        new_btn = gr.Button("New Session", scale=1, variant="secondary")

    gr.Markdown("**Examples** — click any to fill the message box:")
    with gr.Row():
        example_btns = [gr.Button(ex, size="sm", variant="secondary") for ex in EXAMPLES[:4]]
    with gr.Row():
        example_btns += [gr.Button(ex, size="sm", variant="secondary") for ex in EXAMPLES[4:]]

    chatbot = gr.Chatbot(label="Chat", height=380)

    with gr.Row():
        msg_box = gr.Textbox(
            placeholder="Ask me to generate any file, or just chat...",
            label="Message",
            scale=5,
            lines=1,
        )
        send_btn = gr.Button("Send", scale=1, variant="primary")

    gr.Markdown("---\n### Downloads\nGenerated files appear here. Click a filename to download to your Downloads folder.")
    file_output = gr.File(
        label="Generated files",
        file_count="multiple",
        interactive=False,
    )

    # Wire example buttons to fill the message box
    for btn, ex in zip(example_btns, EXAMPLES):
        btn.click(fn=lambda t=ex: t, outputs=msg_box)

    # Send on button click or Enter
    send_btn.click(
        fn=respond,
        inputs=[msg_box, chatbot, thread_input, file_state],
        outputs=[chatbot, file_state, file_output],
    ).then(fn=lambda: "", outputs=msg_box)

    msg_box.submit(
        fn=respond,
        inputs=[msg_box, chatbot, thread_input, file_state],
        outputs=[chatbot, file_state, file_output],
    ).then(fn=lambda: "", outputs=msg_box)

    new_btn.click(
        fn=new_session,
        inputs=[file_state],
        outputs=[chatbot, thread_input, file_output],
    )

if __name__ == "__main__":
    demo.launch()
