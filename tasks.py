from typing import Union
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from io import BytesIO
import os
import random
from running_ollama_easy import ResourceCreator, ResponsePrep, ResponseMidTaskExtract, ResponseMidTaskQuestionsTF, ResponseMidTaskQuestionsMCQ, ResponseDiscussion, BaseModel


class Task:
    def __init__(self, skill: str, difficulty: str, topic: str, content_dict: Union[dict, str, BaseModel] = None):
        """
        Parent class to create different types of tasks for language learning materials.
        
        Args:
            skill (str): The language skill (e.g., "Reading", "Writing", "Speaking", "Listening")
            difficulty (str): The difficulty level (e.g., "A1", "A2", "B1", "B2", "C1")
            topic (str): The topic of the exercise
            content_dict (Union[dict, str]): The content for the task. This can be a dictionary or a string depending on the task type.
        """
        self.skill = skill
        self.difficulty = difficulty
        self.topic = topic
        self.content_dict = content_dict.answer if isinstance(content_dict, (ResponsePrep, ResponseMidTaskExtract, ResponseMidTaskQuestionsTF, ResponseMidTaskQuestionsMCQ, ResponseDiscussion)) else content_dict
        self.answer_key = {}
        self.create_pdf_initial()
           
    def create_pdf_initial(self, packet: BytesIO = None) -> BytesIO:
        self.packet = BytesIO() if packet is None else packet
        self.can = canvas.Canvas(self.packet, pagesize=A4)
        can_width = A4[0]
        can_height = A4[1]
        
        # Add header information
        self.can.setFont("Helvetica", 12)
        self.can.drawRightString(can_width - 20 * mm, 287 * mm, f"{self.skill}: {self.difficulty}")
        self.can.setFont("Helvetica", 18)
        self.can.drawRightString(can_width - 20 * mm, 280 * mm, self.topic)
        return self.packet
    
    
    def create_output_path(self) -> str:
        # Create default filename based on skill, difficulty, and topic
        safe_topic = self.topic.replace(" ", "_").replace("-", "_")
        filename = f"{self.skill}_{self.difficulty}_{safe_topic}_Preparation_Task.pdf"
        current_dir = os.getcwd()
        output_path = os.path.join(current_dir, "resources_edited", "Reading", filename)
        return output_path
         
class PreparationTask(Task):
    """
    A class to create preparation tasks for language learning materials.
    Supports matching exercises with customizable content and formatting.
    """
    
    def __init__(self, skill: str, difficulty: str, topic: str, content_dict: ResponsePrep):
        """
        Initialize a PreparationTask.
        
        Args:
            skill (str): The language skill (e.g., "Reading", "Writing", "Speaking", "Listening")
            difficulty (str): The difficulty level (e.g., "A1", "A2", "B1", "B2", "C1")
            topic (str): The topic of the exercise
            correct_pairs (dict): Dictionary of correct answer pairs. Will contain a key for the labels and a key for the matching answers e.g. {'labels': ['Food Items', 'Descriptions'], 'correct_pairs': {'Spaghetti': 'pasta dish made from dough and sauce', 'Margherita Pizza': 'Italian dish with tomato, mozzarella, and basil', 'Caesar Salad': 'green salad with croutons, parmesan cheese, and Caesar dressing', 'Tiramisu': 'Italian dessert with layers of coffee-soaked ladyfingers and mascarpone'}}
            task_type (str): Type of task (default: "matching")
        """
        super().__init__(skill, difficulty, topic, content_dict)
        self.correct_pairs = self.content_dict["correct_pairs"]
        
    def _shuffle_answers(self):
        """
        Shuffle the answers to create variation in correct answer patterns.
        
        Returns:
            tuple: (shuffled_items, shuffled_answers, answer_key)
        """
        items = list(self.content_dict["correct_pairs"].keys())
        answers = list(self.content_dict["correct_pairs"].values())
        print("Original answers:", answers)
        print("Original items:", items)
        
        # Shuffle the answers to create variation
        random.shuffle(answers)
        
        # Create answer key mapping
        answer_key = {}
        for i, item in enumerate(items):
            correct_answer = self.correct_pairs[item]
            answer_index = answers.index(correct_answer)
            answer_key[str(i+1)] = chr(97 + answer_index)
        
        return items, answers, answer_key
    
    def _create_matching_task_pdf(self, packet: BytesIO = None) -> BytesIO:
        """
        Create a PDF for a matching task.
        
        Returns:
            BytesIO: PDF content as BytesIO object
        """
        
        # Get shuffled content
        items, answers, self.answer_key = self._shuffle_answers()
        
        # Create formatted lists
        items_formatted = [f"{i+1}. …… {item}" for i, item in enumerate(items)]
        answers_formatted = [f"{chr(97+i)}. {answer}" for i, answer in enumerate(answers)]
        
        # Positioning
        x_start = 20 * mm
        x_answers = x_start + 70 * mm
        y_start = 270 * mm
        line_height = 5 * mm
        
        # Draw task title
        self.can.setFont("Helvetica-Bold", 16)
        self.can.drawString(x_start, y_start, "Preparation task")
        
        # Draw instruction
        self.can.setFont("Helvetica", 12)
        instruction = f"Match the items (1–{len(items)}) with the answers (a–{chr(96+len(items))})."
        self.can.drawString(x_start, y_start - line_height*2, instruction)
        
        # Draw headers
        self.can.setFont("Helvetica-Bold", 12)
        self.can.drawString(x_start, y_start - 4 * line_height, "Items")
        self.can.drawString(x_answers, y_start - 4 * line_height, "Answers")
        
        # Draw items and answers
        self.can.setFont("Helvetica", 12)
        for i in range(len(items)):
            self.can.drawString(x_start, y_start - (5 + i) * line_height, items_formatted[i])
            self.can.drawString(x_answers, y_start - (5 + i) * line_height, answers_formatted[i])
        
        # Add answers section
        self._add_answers_section(self.can, x_start, y_start, line_height, len(items))

        self.can.save()
        self.packet.seek(0)
        return self.packet

    def _add_answers_section(self, canvas, x_start, y_start, line_height, num_items):
        """
        Add the answers section to the PDF.
        
        Args:
            canvas: ReportLab canvas object
            x_start: Starting x position
            y_start: Starting y position
            line_height: Height between lines
            num_items: Number of items in the task
        """
        answers_y_start = y_start - (5 + num_items) * line_height - 15 * mm
        
        # Draw Answers section
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawString(x_start, answers_y_start, "Answers:")
        
        # Draw task subtitle
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(x_start, answers_y_start - 8 * mm, "Preparation Task")
        
        # Draw answer key
        canvas.setFont("Helvetica", 12)
        for i in range(num_items):
            answer_line = f"{i+1}. {self.answer_key[str(i+1)]}"
            canvas.drawString(x_start, answers_y_start - (15 + i * 5) * mm, answer_line)
    
    def create_pdf(self, output_path=None):
        """
        Create and save the preparation task PDF.
        
        Args:
            output_path (str, optional): Path to save the PDF. If None, uses default naming.
        
        Returns:
            str: Path to the saved PDF file
        """
        if output_path is None:
            output_path = self.create_output_path()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF content
        pdf_content = self._create_matching_task_pdf()
        
        # Save PDF
        new_pdf = PdfReader(pdf_content)
        output_pdf = PdfWriter()
        output_pdf.add_page(new_pdf.pages[0])
        
        with open(output_path, "wb") as f:
            output_pdf.write(f)
        
        return output_path
    
    def get_answer_key(self):
        """
        Get the answer key for the current task.
        
        Returns:
            dict: Answer key mapping question numbers to answer letters
        """
        return self.answer_key.copy()
    
    def __str__(self):
        """String representation of the PreparationTask."""
        return f"PreparationTask(skill='{self.skill}', difficulty='{self.difficulty}', topic='{self.topic}', items={len(self.correct_pairs)})"
    

class MiddleTask(Task):
    """Class for building English language reading tasks.
    Supports various task types such as extract, true/false questions, multiple choice questions, and ordering tasks.
    """
    def __init__(self, skill: str, difficulty: str, topic: str, task_types: list, extract: str):
        super().__init__(skill, difficulty, topic, content_dict)
        self.task_types = task_types
        self.extract = extract
        
    def display_true_false_questions(self):
        print("True/False Questions:")
        for question, answer in zip(self.questions, self.answers):
            print(f"Q: {question} - A: {'True' if answer else 'False'}")
        pass
        
    def process_extract(self) -> Paragraph:
        print("Processing extract...")
        splitted_extract = self.extract.split("\n") # This will give a list of lines
        processed_extract = "<BR/>".join(splitted_extract)
        p1 = Paragraph(processed_extract)
        p1.wrapOn(self.can, 150*mm, 250*mm)
        return p1
    
    def create_pdf(self, output_path=None):
        if output_path is None:
            output_path = self.create_output_path()
            
        pdf_content = self._create_pdf()
        # Save PDF
        new_pdf = PdfReader(pdf_content)
        output_pdf = PdfWriter()
        output_pdf.add_page(new_pdf.pages[0])
        
        with open(output_path, "wb") as f:
            output_pdf.write(f)
        
        return output_path
        
        
    
    def _create_pdf(self):
        print(f"Creating PDF for {self.task_types[0]} task...")
        # Positioning
        x_start = 20 * mm
        x_answers = x_start + 70 * mm
        y_start = 270 * mm
        line_height = 5 * mm
        
        # Draw task title
        self.can.setFont("Helvetica-Bold", 16)
        self.can.drawString(x_start, y_start, "Intermediate Extract")
        
        # Draw instruction
        self.can.setFont("Helvetica", 12)
        instruction = f"Read the following extract:"
        self.can.drawString(x_start, y_start - line_height*2, instruction)
        
        # Draw extract and get its height
        extract_paragraph = self.process_extract()
        extract_height = extract_paragraph.height
        extract_y_position = y_start - line_height*2 - extract_height  # Starting position for extract
        extract_paragraph.drawOn(self.can, x_start, extract_y_position)
        
        # Calculate next position AFTER the extract
        # Get the actual height of the paragraph
        
        next_y_position = extract_y_position  # Add spacing
        
        # Draw headers (now positioned dynamically)
        self.can.setFont("Helvetica-Bold", 12)
        self.can.drawString(x_start, next_y_position, "Intermediate Task 1")
        
        # Draw items and answers
        self.can.setFont("Helvetica", 12)

        self.can.save()
        self.packet.seek(0)
        return self.packet
        
    pass

class Discussion(Task):
    pass

# Example usage
if __name__ == "__main__":
    # Define the correct city and country pairs
    content_dict = {
    "labels": ["Cities", "Countries"],
    "correct_pairs": {
    "Beijing": "China",
    "Buenos Aires": "Argentina", 
    "Los Angeles": "The United States of America",
    "Amsterdam": "The Netherlands",
    "Mexico City": "Mexico",
    "Seoul": "The Republic of Korea",
    "Christchurch": "New Zealand",
    "Moscow": "Russia"
    }}
    
    # Create a preparation task
    task = PreparationTask(
        skill="Reading",
        difficulty="A1",
        topic="An airport departures board",
        content_dict=content_dict
    )
    
    # Create and save the PDF
    output_path = task.create_pdf()
    print(f"PDF created successfully at: {output_path}")
    print(f"Answer key: {task.get_answer_key()}")

    # Create a different task
    vocabulary_task = PreparationTask(
        skill="Reading",
        difficulty="B1", 
        topic="Business vocabulary",
        content_dict={"labels": ["abbreviation", "title"], "correct_pairs": {"CEO": "Chief Executive Officer", "HR": "Human Resources"}}
    )
    # Create the PDF
    output_path = vocabulary_task.create_pdf()
    print(f"Answer key: {vocabulary_task.get_answer_key()}")
    
    middle_task_test = MiddleTask(
        skill = "Reading",
        difficulty = "A2", 
        topic = "An email from a friend",
        task_types = ["TF"], 
        extract = """
          Hi Samia,
          Quick email to say that sounds like a great idea. Saturday is better for me because I’m meeting my parents on Sunday. So if that’s still good for you, why don’t you come here? Then you can see the new flat and all the work we’ve done on the kitchen since we moved in. We can eat at home and then go for a walk in the afternoon. It’s going to be so good to catch up finally. I want to hear all about your new job!
          Our address is 52 Charles Road, but it’s a bit difficult to find because the house numbers are really strange here. If you turn left at the post office and keep going past the big white house on Charles Road, there’s a small side street behind it with the houses 50–56 in. Don’t ask me why the side street doesn’t have a different name! But call me if you get lost and I’ll come and get you. 
          Let me know if there’s anything you do/don’t like to eat. Really looking forward to seeing you! <BR/>
          See you soon!
          Gregor
          
          
          """
    )
    
    middle_task_test.create_pdf()
    print("Created middle task PDF.")
