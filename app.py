import os
import re
import uuid
import tempfile
import gradio as gr
from agent import chat

TEMP_DIR = os.path.join(tempfile.gettempdir(), "my-first-agent")
os.makedirs(TEMP_DIR, exist_ok=True)

EXAMPLES = [
    "Write a Python script that prints Fibonacci",
    "CSV: Name, Age, City — 3 rows",
    "Markdown README for a Python project",
    "PDF intro about AI agents",
    "Excel: monthly expenses, 5 rows",
    "Word doc cover letter template",
    "Jupyter notebook: import pandas, print Hello World",
]


def respond(message, history, thread_id, known_files):
    thread_id = (thread_id or "").strip() or "default"
    if not message or not message.strip():
        return history, known_files, known_files

    # Detect new files by diffing the temp dir before and after
    before = set(os.listdir(TEMP_DIR))
    try:
        response = chat(message, thread_id=thread_id)
    except Exception as e:
        response = f"Error: {e}"
    after = set(os.listdir(TEMP_DIR))

    new_filenames = after - before
    new_paths = [os.path.join(TEMP_DIR, f) for f in new_filenames if os.path.exists(os.path.join(TEMP_DIR, f))]

    if new_paths:
        names = [os.path.basename(p) for p in new_paths]
        response += f"\n\n**Ready to download:** {', '.join(names)} — scroll down to the Downloads section."

    updated_files = known_files + new_paths
    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response},
    ]
    return history, updated_files, updated_files


def new_session(known_files):
    return [], str(uuid.uuid4())[:8], known_files


with gr.Blocks(title="My First Agent") as demo:
    gr.Markdown("# My First Agent\nChat with your agent. It shows content in chat first — download when you're happy with it.")

    file_state = gr.State([])

    with gr.Row():
        thread_input = gr.Textbox(
            value="default",
            label="Session ID",
            info="Each unique ID is an isolated conversation thread.",
            scale=4,
        )
        new_btn = gr.Button("New Session", scale=1, variant="secondary")

    chatbot = gr.Chatbot(label="Chat", height=400)

    # Example chips between chatbot and input
    with gr.Row():
        example_btns = [gr.Button(ex, size="sm", variant="secondary", scale=1) for ex in EXAMPLES]

    with gr.Row():
        msg_box = gr.Textbox(
            placeholder="Ask me to generate any file, or just chat...",
            label="Message",
            scale=5,
            lines=1,
        )
        send_btn = gr.Button("Send", scale=1, variant="primary")

    with gr.Accordion("Downloads", open=True):
        gr.Markdown("Generated files appear here. Click a filename to download to your Downloads folder.")
        file_output = gr.File(
            label="Generated files",
            file_count="multiple",
            interactive=False,
        )

    # Wire example buttons to fill message box
    for btn, ex in zip(example_btns, EXAMPLES):
        btn.click(fn=lambda t=ex: t, outputs=msg_box)

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
