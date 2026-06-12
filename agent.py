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
    "You can create CSV, Markdown, Python scripts, PDF, Excel, Word documents, and Jupyter notebooks. "
    "Follow these rules:\n"
    "1. For code or text content (Python, Markdown, Jupyter): ALWAYS show the full content inline in the chat first, "
    "then ask the user if they want it saved as a file before calling any tool.\n"
    "2. For data files (CSV, Excel): you may generate them directly since the content is tabular and less readable inline, "
    "but still describe what you created.\n"
    "3. For PDF and Word docs: generate directly but show a preview of the text content in the chat.\n"
    "4. When a file is saved, always state the full file path exactly as returned by the tool.\n"
    "5. If a request is ambiguous, ask a clarifying question before doing anything."
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
