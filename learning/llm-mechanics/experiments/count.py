import sys, tiktoken
from docx import Document
from pypdf import PdfReader

enc = tiktoken.get_encoding("o200k_base")

def read_text(path):
    if path.endswith(".pdf"):
        return "\n".join(page.extract_text() for page in PdfReader(path).pages)
    if path.endswith(".docx"):
        doc = Document(path)
        cells = [cell.text for table in doc.tables for row in table.rows for cell in row.cells]
        return "\n".join([p.text for p in doc.paragraphs] + cells)
    return open(path, encoding="utf-8").read()  # any plain-text file

def report(path):
    try:
        text = read_text(path)
    except UnicodeDecodeError:
        print(f"{path}: skipped, not plain text, .docx or .pdf")
        return
    n = len(enc.encode(text))
    if n == 0:
        print(f"{path}: no text found (a scanned PDF has no text layer)")
        return
    print(f"{path}: {n} tokens, {len(text)/n:.1f} chars/token, "
          f"{len(text.split())/n:.2f} words/token")

for path in sys.argv[1:]:
    report(path)
