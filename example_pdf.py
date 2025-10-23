from typing import Union
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.platypus import PageBreak
from io import BytesIO
import os
import random


example_pdf = BytesIO()
c = canvas.Canvas(example_pdf, pagesize=A4)
width, height = A4
styles = {
    'default': ParagraphStyle(
        'default',
        fontName='Helvetica',
        fontSize=12,
        leading=14,
        spaceAfter=10,
    )
}
text = """This is an example PDF document. It contains multiple pages with text content.
Each page is generated using the ReportLab library in Python.
This document serves as a sample for adding hyperlinks to specific keywords.
The keyword we will be linking to is 'video'.
Feel free to explore the content and see how hyperlinks can enhance the document's interactivity.
This is page 2 of the example PDF. The keyword 'video' appears here as well.
Adding hyperlinks to keywords can be very useful in documents."""

for i in range(3):
    p = Paragraph(text, styles['default'])
    p.wrapOn(c, width - 2 * 72, height - 2 * 72)
    p.drawOn(c, 72, height - 72 - p.height)
    c.showPage()
    
c.save()
example_pdf.seek(0)
output_path = "example_with_link.pdf"
with open(output_path, "wb") as f:
    f.write(example_pdf.read())