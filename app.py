import os
import uuid
import tempfile
import gradio as gr
from agent import chat

TEMP_DIR = os.path.join(tempfile.gettempdir(), "my-first-agent")
os.makedirs(TEMP_DIR, exist_ok=True)

EXAMPLES = [
    ("🐍 Python", "Write a Python script that prints the Fibonacci sequence"),
    ("📊 CSV", "Generate a CSV with columns Name, Age, City and 3 sample rows"),
    ("📝 Markdown", "Create a Markdown README template for a Python project"),
    ("📄 PDF", "Generate a PDF with a short intro about AI agents"),
    ("📈 Excel", "Create an Excel file tracking monthly expenses with 5 rows"),
    ("📃 Word", "Write a Word document with a simple cover letter template"),
    ("📓 Jupyter", "Create a Jupyter notebook that imports pandas and prints Hello World"),
]

PLACEHOLDER_HTML = """
<div style="display:flex; flex-direction:column; align-items:center; justify-content:center;
            height:100%; padding: 40px 20px; gap: 20px; color:#555;">
  <div style="font-size:2rem;">🤖</div>
  <div style="font-size:1.1rem; font-weight:600; color:#333;">What would you like to create?</div>
  <div style="display:flex; flex-wrap:wrap; gap:10px; justify-content:center; max-width:680px;">
    <span style="padding:8px 14px;border:1px solid #ddd;border-radius:20px;font-size:0.85rem;background:#f9f9f9;">🐍 Python script</span>
    <span style="padding:8px 14px;border:1px solid #ddd;border-radius:20px;font-size:0.85rem;background:#f9f9f9;">📊 CSV file</span>
    <span style="padding:8px 14px;border:1px solid #ddd;border-radius:20px;font-size:0.85rem;background:#f9f9f9;">📝 Markdown doc</span>
    <span style="padding:8px 14px;border:1px solid #ddd;border-radius:20px;font-size:0.85rem;background:#f9f9f9;">📄 PDF</span>
    <span style="padding:8px 14px;border:1px solid #ddd;border-radius:20px;font-size:0.85rem;background:#f9f9f9;">📈 Excel sheet</span>
    <span style="padding:8px 14px;border:1px solid #ddd;border-radius:20px;font-size:0.85rem;background:#f9f9f9;">📃 Word doc</span>
    <span style="padding:8px 14px;border:1px solid #ddd;border-radius:20px;font-size:0.85rem;background:#f9f9f9;">📓 Jupyter notebook</span>
  </div>
  <div style="font-size:0.8rem;color:#aaa;">Click an example below or type your own request</div>
</div>
"""


def respond(message, history, thread_id, known_files):
    thread_id = (thread_id or "").strip() or "default"
    if not message or not message.strip():
        return history, known_files, known_files, gr.update(visible=False)

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
    return history, updated_files, updated_files, gr.update(visible=False)


def new_session(known_files):
    return [], str(uuid.uuid4())[:8], known_files, gr.update(visible=True)


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

    chatbot = gr.Chatbot(label="Chat", height=420, placeholder=PLACEHOLDER_HTML)

    with gr.Row(visible=True) as example_row:
        btns = [gr.Button(label, size="sm", variant="secondary", scale=1) for label, _ in EXAMPLES]

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

    for btn, (_, prompt) in zip(btns, EXAMPLES):
        btn.click(fn=lambda p=prompt: p, outputs=msg_box)

    send_btn.click(
        fn=respond,
        inputs=[msg_box, chatbot, thread_input, file_state],
        outputs=[chatbot, file_state, file_output, example_row],
    ).then(fn=lambda: "", outputs=msg_box)

    msg_box.submit(
        fn=respond,
        inputs=[msg_box, chatbot, thread_input, file_state],
        outputs=[chatbot, file_state, file_output, example_row],
    ).then(fn=lambda: "", outputs=msg_box)

    new_btn.click(
        fn=new_session,
        inputs=[file_state],
        outputs=[chatbot, thread_input, file_output, example_row],
    )

if __name__ == "__main__":
    demo.launch()
