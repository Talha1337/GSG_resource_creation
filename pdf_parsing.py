# Re-run the extraction pipeline on the re-uploaded file
import fitz  # PyMuPDF
import re
import os
import subprocess
import sys
from pprint import pprint


# Load the re-uploaded PDF
pdf_path = os.getcwd() + "/resources/Reading/LearnEnglish-Reading-A1-An-airport-departures-board.pdf"
doc = fitz.open(pdf_path)
full_text = "\n".join([page.get_text() for page in doc])
print(full_text[:1500])
doc.close()

# Extract title and level
def extract_title_and_level(text):
    title_match = re.search(r'Reading:\s*(A\d)\s*\n(.*?)\n', text)
    if title_match:
        level = title_match.group(1).strip()
        title = title_match.group(2).strip()
        return level, title
    return None, None

# Extract major sections
def split_reading_pdf_sections(text):
    sections = {}
    prep_pattern = r'Preparation task(.*?)Reading text:'
    prep_match = re.search(prep_pattern, text, re.DOTALL)
    # add some preprocessing to remove the confusingly fitted headings
    processed_output = prep_match.group(1).strip()
    processed_output = processed_output.replace("Cities", "")
    processed_output = processed_output.replace("Countries", "")
    if prep_match:
        sections["Preparation Task"] = processed_output
    return sections

# Run extractions
parsed_sections = split_reading_pdf_sections(full_text)
print("PARSED SECTION : ")
print(parsed_sections)
print(re.search("Cities", parsed_sections["Preparation Task"]))
reading_level, reading_title = extract_title_and_level(full_text)
parsed_sections["Level"] = reading_level
parsed_sections["Title"] = reading_title

# Output the specific parts we care about
document_summary_prep_task = {
    "Title": reading_title,
    "Level": reading_level,
    "Preparation Task": parsed_sections.get("Preparation Task", "")
}

# PARSING DONE BY THIS POINT

pprint(f"Preparation Task: {document_summary_prep_task['Preparation Task']}")




def generate_matching_task(document_summary):
    topic = document_summary["Title"]
    level = document_summary["Level"]
    
    prompt = f"""
    
    You are an expert in creating matching tasks for English language learners.
    Your task is to create a matching task based on the provided preparation task.
    You should provide as output a new matching task, relating to the topic "{topic}."
    
    An example of a matching task is:
    
    -----------------------
    
    {document_summary_prep_task["Preparation Task"]}

    -----------------------
    
    
    """
    print(prompt)
    result = subprocess.run(
        ["ollama", "run", "deepseek-r1", f"'{prompt}'"],
        capture_output=True
    )

    output = result.stdout.decode()
    
    return output

final_output = generate_matching_task(document_summary_prep_task)
print("---RESPONSE---")
print(final_output)


