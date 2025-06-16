from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder
# This script adds a hyperlink annotation to the first page of a PDF file.
reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add hyperlink annotation to the first page
link = AnnotationBuilder.link(
    rect=(100, 100, 200, 120),  # position on the page
    url="https://example.com"
)
writer.add_annotation(0, link)

with open("output.pdf", "wb") as f:
    writer.write(f)
