from crewai.tools import tool
import os

# Add imports for docx and pdf reading
try:
    from docx import Document
except ImportError:
    Document = None
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

@tool("Folder Reader Tool")
def read_folder_contents(folder_path: str = "common") -> str:
    """Reads and returns content of all text-like files from a folder, including .txt, .md, .log, .docx, .pdf"""
    results = []
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if filename.endswith((".txt", ".md", ".log")):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                results.append(f"--- {filename} ---\n{content}")
            except Exception as e:
                results.append(f"--- {filename} ---\n[Error reading file: {e}]")
        elif filename.endswith(".docx") and Document:
            try:
                doc = Document(full_path)
                content = "\n".join([para.text for para in doc.paragraphs])
                results.append(f"--- {filename} ---\n{content}")
            except Exception as e:
                results.append(f"--- {filename} ---\n[Error reading DOCX: {e}]")
        elif filename.endswith(".pdf") and PyPDF2:
            try:
                with open(full_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    content = "\n".join([page.extract_text() or "" for page in reader.pages])
                results.append(f"--- {filename} ---\n{content}")
            except Exception as e:
                results.append(f"--- {filename} ---\n[Error reading PDF: {e}]")
        else:
            # Try reading as text, fallback to binary note
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                results.append(f"--- {filename} ---\n{content}")
            except Exception:
                results.append(f"--- {filename} ---\n[Unsupported or binary file]")
    return "\n\n".join(results)
