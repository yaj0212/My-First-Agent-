# My First Agent

A conversational AI agent built with **LangChain**, **LangGraph**, and **Deep Agents** (Python). Supports multi-turn chat, multimodal input, and on-demand file generation.

## Features

- Multi-turn conversation with persistent memory (per thread)
- Multimodal support via Claude (text + images)
- File generation tools:
  - CSV
  - Markdown
  - Python scripts
  - *(more coming: PDF, DOCX, XLSX, .ipynb)*
- Platform integrations via MCP *(coming soon: Gmail, GitHub, LinkedIn, etc.)*

## Tech Stack

| Layer | Library |
|---|---|
| LLM | [Anthropic Claude](https://www.anthropic.com) via `langchain-anthropic` |
| Orchestration | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| Agent framework | [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) |
| Observability | [LangSmith](https://smith.langchain.com) |
| Tool protocol | [MCP](https://modelcontextprotocol.io) via `langchain-mcp-adapters` |

## Project Structure

```
My-First-Agent/
├── agent.py           # Main agent entry point
├── tools/
│   └── file_tools.py  # File generation tools
├── output/            # Generated files land here (gitignored)
├── requirements.txt
├── .env.example       # API key template
└── .gitignore
```

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yaj0212/My-First-Agent-.git
cd My-First-Agent-
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

```bash
cp .env.example .env
# Open .env and fill in your keys
```

Your `.env` file should look like:

```
ANTHROPIC_API_KEY=your_anthropic_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=my-agent
```

> **Never commit your `.env` file.** It is gitignored by default.

### 5. Run the agent

```bash
python agent.py
```

## Usage

```
Agent ready. Type 'quit' to exit.

You: generate a CSV with columns Name, Age, City and 3 sample rows
Agent: CSV saved to output/people.csv

You: write a Python script that prints the Fibonacci sequence
Agent: Python file saved to output/fibonacci.py

You: quit
```

Generated files are saved to the `output/` folder.

## Roadmap

- [ ] PDF, DOCX, XLSX, `.ipynb` generation
- [ ] Gmail integration
- [ ] GitHub integration
- [ ] LinkedIn integration
- [ ] Web UI (Gradio or Streamlit)

## License

MIT
