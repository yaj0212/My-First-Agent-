import os
import uuid
import tempfile
import gradio as gr
from agent import chat

TEMP_DIR = os.path.join(tempfile.gettempdir(), "my-first-agent")
os.makedirs(TEMP_DIR, exist_ok=True)

EXAMPLES = [
    ("🐍 Python script", "Write a Python script that prints the Fibonacci sequence"),
    ("📊 CSV file", "Generate a CSV with columns Name, Age, City and 3 sample rows"),
    ("📝 Markdown doc", "Create a Markdown README template for a Python project"),
    ("📄 PDF", "Generate a PDF with a short intro about AI agents"),
    ("📈 Excel sheet", "Create an Excel file tracking monthly expenses with 5 rows"),
    ("📃 Word doc", "Write a Word document with a simple cover letter template"),
    ("📓 Jupyter notebook", "Create a Jupyter notebook that imports pandas and prints Hello World"),
]


def respond(message, history, thread_id, known_files):
    thread_id = (thread_id or "").strip() or "default"
    if not message or not message.strip():
        return (history, known_files, known_files,
                gr.update(visible=True), gr.update(visible=False))

    before = set(os.listdir(TEMP_DIR))
    try:
        response = chat(message, thread_id=thread_id)
    except Exception as e:
        response = f"Error: {e}"
    after = set(os.listdir(TEMP_DIR))

    new_paths = [
        os.path.join(TEMP_DIR, f) for f in (after - before)
        if os.path.exists(os.path.join(TEMP_DIR, f))
    ]
    if new_paths:
        names = [os.path.basename(p) for p in new_paths]
        response += f"\n\n**Ready to download:** {', '.join(names)} — see the Downloads section below."

    updated_files = known_files + new_paths
    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response},
    ]
    return (history, updated_files, updated_files,
            gr.update(visible=False), gr.update(visible=True))


def new_session(known_files):
    return ([], str(uuid.uuid4())[:8], known_files,
            gr.update(visible=True), gr.update(visible=False))


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

    # Welcome panel — replaces chatbot when session is empty
    with gr.Group(visible=True) as welcome_panel:
        gr.HTML("""
        <div style="text-align:center; padding: 48px 20px 24px; color:#333;">
          <div style="font-size:2.2rem; margin-bottom:12px;">🤖</div>
          <div style="font-size:1.1rem; font-weight:600; margin-bottom:6px;">What would you like to create?</div>
          <div style="font-size:0.82rem; color:#999;">Click an option to get started, or type your own request below</div>
        </div>
        """)
        with gr.Row():
            btns = [gr.Button(label, variant="secondary", scale=1) for label, _ in EXAMPLES]
        gr.HTML("<div style='height:48px'></div>")

    # Chatbot — shown only after first message
    chatbot = gr.Chatbot(label="Chat", height=420, visible=False)

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

    # Example buttons: fill message box then auto-submit
    for btn, (_, prompt) in zip(btns, EXAMPLES):
        btn.click(fn=lambda p=prompt: p, outputs=msg_box).then(
            fn=respond,
            inputs=[msg_box, chatbot, thread_input, file_state],
            outputs=[chatbot, file_state, file_output, welcome_panel, chatbot],
        ).then(fn=lambda: "", outputs=msg_box)

    send_btn.click(
        fn=respond,
        inputs=[msg_box, chatbot, thread_input, file_state],
        outputs=[chatbot, file_state, file_output, welcome_panel, chatbot],
    ).then(fn=lambda: "", outputs=msg_box)

    msg_box.submit(
        fn=respond,
        inputs=[msg_box, chatbot, thread_input, file_state],
        outputs=[chatbot, file_state, file_output, welcome_panel, chatbot],
    ).then(fn=lambda: "", outputs=msg_box)

    new_btn.click(
        fn=new_session,
        inputs=[file_state],
        outputs=[chatbot, thread_input, file_output, welcome_panel, chatbot],
    )

if __name__ == "__main__":
    demo.launch()
