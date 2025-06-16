from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import sys
import fitz  # PyMuPDF

# Step 1: Generate a basic PDF with the target keyword
def generate_sample_pdf(filename, keyword):
    c = canvas.Canvas(filename, pagesize=A4)
    text = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 3) + f" {keyword} " + \
           ("Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. " * 2)
    c.drawString(72, 800, text)
    c.save()

# Step 2: Add a hyperlink to the keyword using PyMuPDF
def add_link_to_keyword(pdf_path, output_path, keyword, url):
    doc = fitz.open(pdf_path)
    found = False

    for page in doc:
        text_instances = page.search_for(keyword)
        for inst in text_instances:
            page.insert_link({
                "from": inst,
                "uri": url,
                "kind": fitz.LINK_URI
            })
            found = True
            break
    doc.save(output_path)
    doc.close()

    if found:
        print(f'✅ Added link to "{keyword}" in: {os.path.basename(pdf_path)}')
    else:
        print(f'⚠️ Keyword not found in: {os.path.basename(pdf_path)}')
        
# Step 3: Process a folder of PDFs and add links to the specified keyword
folder_path = "resources"
keyword = "lorem"
url = "https://example.com"

process_folder(folder_path, keyword, url)
