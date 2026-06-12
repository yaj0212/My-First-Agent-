import csv
import os
from langchain_core.tools import tool

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@tool
def generate_csv(filename: str, headers: list[str], rows: list[list]) -> str:
    """Generate a CSV file with the given headers and rows. Returns the file path."""
    path = os.path.join(OUTPUT_DIR, filename if filename.endswith(".csv") else filename + ".csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return f"CSV saved to {path}"


@tool
def generate_markdown(filename: str, content: str) -> str:
    """Generate a Markdown (.md) file with the given content. Returns the file path."""
    path = os.path.join(OUTPUT_DIR, filename if filename.endswith(".md") else filename + ".md")
    with open(path, "w") as f:
        f.write(content)
    return f"Markdown saved to {path}"


@tool
def generate_python_file(filename: str, code: str) -> str:
    """Generate a Python (.py) file with the given code. Returns the file path."""
    path = os.path.join(OUTPUT_DIR, filename if filename.endswith(".py") else filename + ".py")
    with open(path, "w") as f:
        f.write(code)
    return f"Python file saved to {path}"
