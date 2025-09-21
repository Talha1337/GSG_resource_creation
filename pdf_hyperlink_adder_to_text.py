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
            break  # Stop after the first instance
    doc.save(output_path)
    doc.close()

    if found:
        print(f'✅ Added link to "{keyword}" in: {os.path.basename(pdf_path)}')
    else:
        print(f'⚠️ Keyword not found in: {os.path.basename(pdf_path)}')  
        
def parse_filename(filename):
    # Extract the keyword from the filename
    base_name = os.path.splitext(filename)[0]
    parts = base_name.split('-')
    if len(parts) > 3:
        assert parts[2].lower() in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2'], "Invalid level in filename"
        assert parts[1].lower() in ['speaking', 'listening', 'reading', 'writing'], "Invalid skill in filename"
        return (parts[2], "-".join(parts[3:]).lower())  # Assuming the keyword is the fourth part
    return None
        
# Step 3: Process a folder of PDFs and add links to the specified keyword
folder_path = "resources/Speaking"
keyword = "video"
output_folder = "resources/Speaking_modified"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
for filename in os.listdir(folder_path):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(folder_path, filename)
        output_path = os.path.join(output_folder, filename)

        print(f'Processing file: {filename}')
        filename_keywords = parse_filename(filename)
        print(f"current keywords: {filename_keywords}")
        level = filename_keywords[0] if filename_keywords else None
        topic = filename_keywords[1] if filename_keywords else None
        if not level or not keyword:
            print(f"Skipping file {filename} due to missing level or keyword.")
            continue
        url_to_add = f"https://learnenglish.britishcouncil.org/skills/speaking/{level}-speaking/{topic}"
        print(f'Adding link to keyword "{keyword}" in {filename} with URL: {url_to_add}')
        add_link_to_keyword(pdf_path, output_path, keyword, url_to_add)

        # add_link_to_keyword(pdf_path, output_path, keyword, url)
    else:
        print(f'Skipping non-PDF file: {filename}')
