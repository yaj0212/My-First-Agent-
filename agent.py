import os
from dotenv import load_dotenv

load_dotenv()

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage

from tools.file_tools import (
    generate_csv,
    generate_markdown,
    generate_python_file,
    generate_pdf,
    generate_excel,
    generate_word_doc,
    generate_notebook,
)

SYSTEM = SystemMessage(content=(
    "You are a helpful file-generation assistant. "
    "You can create CSV, Markdown, Python scripts, PDF, Excel, Word documents, and Jupyter notebooks.\n\n"
    "Follow these rules strictly:\n"
    "1. ALWAYS show the full content inline in the chat first for every file type — "
    "code blocks for Python/Markdown/Jupyter, a formatted table for CSV/Excel, "
    "and the full text for PDF/Word.\n"
    "2. After showing the content, ask ONLY: 'Does this look good, or would you like any changes?'\n"
    "3. If the user confirms it looks good, or says yes/download/save → call the file generation tool immediately.\n"
    "4. If the user asks for changes → update the content, show the revised version, then ask again.\n"
    "5. Never offer 'modify or download or both' — just ask if they want changes first, then save on confirmation.\n"
    "6. If a request is ambiguous, ask a clarifying question before generating anything."
))

model_name = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
llm = ChatAnthropic(
    model=model_name,
    api_key=os.environ["ANTHROPIC_API_KEY"],
)

tools = [
    generate_csv,
    generate_markdown,
    generate_python_file,
    generate_pdf,
    generate_excel,
    generate_word_doc,
    generate_notebook,
]
llm_with_tools = llm.bind_tools(tools)


def call_model(state: MessagesState):
    response = llm_with_tools.invoke([SYSTEM] + state["messages"])
    return {"messages": [response]}


def should_continue(state: MessagesState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


tool_node = ToolNode(tools)

graph = StateGraph(MessagesState)
graph.add_node("agent", call_model)
graph.add_node("tools", tool_node)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

memory = MemorySaver()
app = graph.compile(checkpointer=memory)


def chat(user_input: str, thread_id: str = "default") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
    )
    return result["messages"][-1].content


if __name__ == "__main__":
    print("Agent ready. Type 'quit' to exit.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue
        try:
            response = chat(user_input)
            print(f"Agent: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")
