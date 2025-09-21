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
    # Extract Preparation Task
    prep_pattern = r'Preparation task(.*?)Reading text:'
    prep_match = re.search(prep_pattern, text, re.DOTALL)
    if prep_match:
        processed_output = prep_match.group(1).strip()
        processed_output = processed_output.replace("Cities", "")
        processed_output = processed_output.replace("Countries", "")
        sections["Preparation Task"] = processed_output
    
    # Look for answers in the entire text - try multiple locations
    print("DEBUG: Looking for answers in the entire PDF text...")
    
    # Try to find answers at the end of the document
    ans_patterns = [
        r'Answers(.*?)(?:©|$)',
        r'Answer(.*?)(?:©|$)',
        r'Key(.*?)(?:©|$)',
        r'(\d+\.\s*[a-h])',  # Direct number-letter pairs
    ]
    
    for pattern in ans_patterns:
        ans_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if ans_match:
            answers_text = ans_match.group(1).strip()
            if answers_text:  # Only use if we found actual content
                sections["Answers"] = answers_text
                print(f"DEBUG: Found answers with pattern '{pattern}':")
                print(answers_text)
                break
    
    # If no answers found, let's print the last part of the text to see what's there
    if "Answers" not in sections:
        print("DEBUG: No answers found with patterns. Last 500 characters of text:")
        print(text[-500:])
    
    return sections

# Run extractions
parsed_sections = split_reading_pdf_sections(full_text)
print("PARSED SECTIONS : ")
print(parsed_sections)
print("--------------------------------")
for section in parsed_sections:
    print(f"Section: {section}")

print("--------------------------------")

reading_level, reading_title = extract_title_and_level(full_text)
parsed_sections["Level"] = reading_level
parsed_sections["Title"] = reading_title

document_summary_prep_task = {
    "Title": reading_title,
    "Level": reading_level,
    "Preparation Task": parsed_sections.get("Preparation Task", ""),
    "Answers": parsed_sections.get("Answers", "")
}

pprint(f"Preparation Task: {document_summary_prep_task['Preparation Task']}")
pprint(f"Answers: {document_summary_prep_task['Answers']}")

# --- New: Parse answers into a dictionary ---
def parse_answer_pairs(answers_text):
    print(f"DEBUG: Parsing answers text: '{answers_text}'")
    # Only use lines between 'Preparation task' and the next 'Task' heading
    relevant = ''
    m = re.search(r'Preparation task\s*(.*?)(?:Task|$)', answers_text, re.DOTALL | re.IGNORECASE)
    if m:
        relevant = m.group(1)
    else:
        relevant = answers_text
    print(f"DEBUG: Relevant answer lines: '{relevant}'")
    # Try multiple patterns for different answer formats
    patterns = [
        r'(\d+)\.\s*([a-zA-Z])',  # 1. a, 2. b, etc.
        r'(\d+)\s*-\s*([a-zA-Z])',  # 1-a, 2-b, etc.
        r'(\d+)\s*:\s*([a-zA-Z])',  # 1:a, 2:b, etc.
        r'(\d+)\s*([a-zA-Z])',  # 1a, 2b, etc.
    ]
    for pattern in patterns:
        pairs = re.findall(pattern, relevant)
        if pairs:
            print(f"DEBUG: Found pairs with pattern '{pattern}': {pairs}")
            answer_dict = {num: letter for num, letter in pairs}
            return answer_dict
    print("DEBUG: No pairs found with any pattern")
    return {}

def create_word_mapping_dict(prep_task_text, answer_dict):
    print(f"DEBUG: Creating word mapping from prep task: '{prep_task_text[:200]}...'")
    
    # Extract the lists from preparation task
    # Look for numbered items (1. ... 2. ... etc.)
    numbered_items = re.findall(r'(\d+)\.\s*([^\n]+)', prep_task_text)
    print(f"DEBUG: Numbered items found: {numbered_items}")
    
    # Look for lettered items (a. ... b. ... etc.)
    lettered_items = re.findall(r'([a-h])\.\s*([^\n]+)', prep_task_text)
    print(f"DEBUG: Lettered items found: {lettered_items}")
    
    # Create mappings
    number_to_word = {num: word.strip() for num, word in numbered_items}
    letter_to_word = {letter: word.strip() for letter, word in lettered_items}
    
    # Create final dictionary mapping the actual words
    word_mapping = {}
    for num, letter in answer_dict.items():
        if num in number_to_word and letter in letter_to_word:
            # Clean both key and value by removing punctuation and extra characters
            clean_key = re.sub('[^a-zA-Z\s]+', '', number_to_word[num]).strip()
            clean_value = re.sub('[^a-zA-Z\s]+', '', letter_to_word[letter]).strip()
            word_mapping[clean_key] = clean_value
    
    return word_mapping

answer_dict = parse_answer_pairs(document_summary_prep_task["Answers"])
print("---ANSWER DICTIONARY (number-letter pairs)---")
print(answer_dict)

# Create the word mapping dictionary
word_mapping_dict = create_word_mapping_dict(document_summary_prep_task["Preparation Task"], answer_dict)
print("---FINAL WORD MAPPING DICTIONARY---")
print(word_mapping_dict)

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




