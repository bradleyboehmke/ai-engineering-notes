import sys, tiktoken
from pypdf import PdfReader

enc = tiktoken.get_encoding("o200k_base")

def read_text(path):
    if path.endswith(".pdf"):
        return "\n".join(page.extract_text() for page in PdfReader(path).pages)
    return open(path, encoding="utf-8").read()

for path in sys.argv[1:]:
    text = read_text(path)
    n = len(enc.encode(text))
    print(f"{path}: {n} tokens, {len(text)/n:.1f} chars/token, "
          f"{len(text.split())/n:.2f} words/token")