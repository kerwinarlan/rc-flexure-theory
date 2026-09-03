"""NSCP 2015 PDF Knowledge Extractor and Study System.

Extracts scanned PDF pages using PyMuPDF + Tesseract OCR into a structured, searchable Markdown knowledge base.
"""

import os
import re
import subprocess
import sys
import pymupdf

PDF_PATH = "/Users/kerwinarlan/Downloads/PDFs/NSCP-2015.pdf"
KB_DIR = os.path.expanduser("/Users/kerwinarlan/github/rc-flexure-theory/nscp2015_knowledge_base")


def ocr_page(doc: pymupdf.Document, page_num: int) -> str:
    """Run Tesseract OCR on a specific page number (1-indexed)."""
    if page_num < 1 or page_num > len(doc):
        raise ValueError(f"Page number {page_num} out of bounds (1-{len(doc)}).")

    page = doc[page_num - 1]
    pix = page.get_pixmap(dpi=150)
    temp_img = f"/private/tmp/nscp_page_{page_num}.png"
    temp_out = f"/private/tmp/nscp_page_{page_num}_out"

    pix.save(temp_img)
    try:
        subprocess.run(["tesseract", temp_img, temp_out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        out_txt = temp_out + ".txt"
        if os.path.exists(out_txt):
            with open(out_txt, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            os.remove(out_txt)
            if os.path.exists(temp_img):
                os.remove(temp_img)
            return text.strip()
    except Exception as err:
        print(f"OCR Error on page {page_num}: {err}")
    
    if os.path.exists(temp_img):
        os.remove(temp_img)
    return ""


def build_knowledge_base(start_page: int, end_page: int, output_filename: str) -> str:
    """OCR a page range and save to Markdown knowledge base."""
    os.makedirs(KB_DIR, exist_ok=True)
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"NSCP 2015 PDF not found at {PDF_PATH}")

    doc = pymupdf.open(PDF_PATH)
    out_path = os.path.join(KB_DIR, output_filename)

    print(f"Extracting pages {start_page} to {end_page} from {PDF_PATH} into {out_path}...")
    pages_text = []

    for p in range(start_page, end_page + 1):
        print(f"Processing Page {p}/{len(doc)}...", end="\r")
        text = ocr_page(doc, p)
        if text:
            header = f"\n\n<!-- PAGE {p} -->\n## NSCP 2015 - Page {p}\n\n"
            pages_text.append(header + text)

    doc.close()
    full_content = "\n".join(pages_text)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# NSCP 2015 Knowledge Base Extract (Pages {start_page}-{end_page})\n")
        f.write(full_content)

    print(f"\nSaved {len(pages_text)} pages to {out_path} ({len(full_content)} chars)")
    return out_path


def search_knowledge_base(query: str) -> list[tuple[str, str]]:
    """Search extracted Markdown knowledge base files for a keyword or regex."""
    if not os.path.exists(KB_DIR):
        print("Knowledge base directory does not exist yet.")
        return []

    results = []
    pattern = re.compile(query, re.IGNORECASE)

    for fname in os.listdir(KB_DIR):
        if fname.endswith(".md"):
            fpath = os.path.join(KB_DIR, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            blocks = content.split("<!-- PAGE ")
            for b in blocks[1:]:
                lines = b.split("\n", 1)
                page_id = lines[0].split(" -->")[0]
                text = lines[1] if len(lines) > 1 else ""
                if pattern.search(text):
                    results.append((f"Page {page_id} ({fname})", text[:300].strip()))

    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--search":
        q = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "flexure"
        print(f"Searching NSCP 2015 KB for '{q}'...")
        res = search_knowledge_base(q)
        for loc, excerpt in res:
            print(f"\n--- Found in {loc} ---")
            print(excerpt)
    elif len(sys.argv) > 1 and sys.argv[1] == "--sample":
        # Sample extraction of pages 100-102 (Chapter 2 loads)
        build_knowledge_base(100, 102, "chapter_2_sample.md")
    else:
        print("NSCP 2015 Indexer Ready.")
        print("Usage:")
        print("  python3 nscp_indexer.py --sample         # Extract sample pages 100-102")
        print("  python3 nscp_indexer.py --search 'query' # Search knowledge base")
