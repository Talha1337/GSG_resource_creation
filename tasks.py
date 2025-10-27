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
from running_ollama_easy import ResourceCreator, ResponsePrep, ResponseMidTask, ResponseMidTaskQuestionsMCQ, ResponseDiscussion, BaseModel


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
        if content_dict is None:
            print("No content dictionary provided. We will attempt to generate it now...")
        self.content_dict = content_dict.answer if isinstance(content_dict, (ResponsePrep, ResponseMidTask, ResponseMidTaskQuestionsMCQ, ResponseDiscussion)) else content_dict
        self.answer_key = {}
        self.section = "default"
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
        filename = f"{self.skill}_{self.difficulty}_{safe_topic}_{self.section}.pdf"
        current_dir = os.getcwd()
        output_path = os.path.join(current_dir, "resources_edited", "Reading", filename)
        return output_path
         
class PreparationTask(Task):
    """
    A class to create preparation tasks for language learning materials.
    Supports matching exercises with customizable content and formatting.
    """
    
    def __init__(self, skill: str = None, difficulty: str = None, topic: str = None, content_dict: ResponsePrep = None):
        """
        Initialize a PreparationTask.
        
        Args:
            skill (str): The language skill (e.g., "Reading", "Writing", "Speaking", "Listening")
            difficulty (str): The difficulty level (e.g., "A1", "A2", "B1", "B2", "C1")
            topic (str): The topic of the exercise
            correct_pairs (dict): Dictionary of correct answer pairs. Will contain a key for the topic, a key for the labels and a key for the matching answers 
            e.g. {'topic': Food, 'labels': ['Food Items', 'Descriptions'], 'correct_pairs': {'Spaghetti': 'pasta dish made from dough and sauce', 'Margherita Pizza': 'Italian dish with tomato, mozzarella, and basil', 'Caesar Salad': 'green salad with croutons, parmesan cheese, and Caesar dressing', 'Tiramisu': 'Italian dessert with layers of coffee-soaked ladyfingers and mascarpone'}}
            task_type (str): Type of task (default: "matching")
        """
        super().__init__(skill, difficulty, topic, content_dict)
        self.section = "Preparation_Task"
        
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
            correct_answer = self.content_dict["correct_pairs"][item]
            answer_index = answers.index(correct_answer)
            answer_key[str(i+1)] = chr(97 + answer_index)
        
        return items, answers, answer_key
    
    def _create_matching_task_pdf(self, packet: BytesIO = None) -> BytesIO:
        """
        Create a PDF for a matching task.
        
        Returns:
            BytesIO: PDF content as BytesIO object
        """
        
        if packet is None:
            self.create_pdf_initial()
        
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
        
        # Save the canvas
        self.can.save()
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
        self.packet.seek(0)
        self.can.save()
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
    def __init__(self, skill: str = None, difficulty: str = None, topic: str = None, task_types: list = None, content_dict: Union[ResponseMidTask, dict] = None):
        """
        Initialize the MiddleTask with the given parameters.
        Args:
            skill (str): The language skill (e.g., "Reading", "Writing", "Speaking", "Listening")
            difficulty (str): The difficulty level (e.g., "A1", "A2", "B1", "B2", "C1")
            topic (str): The topic of the exercise
            task_types (list): List of task types to include (e.g., ["TF", "MCQ", "Ordering"])
            extract (str): The text extract for the reading task
            content_dict (Union[ResponseMidTask, dict], optional): Additional content for the task.
        """
        super().__init__(skill, difficulty, topic, content_dict)
        if content_dict is None:
            print("No content dictionary")
            return None
        self.content_dict = content_dict.answer if isinstance(content_dict, ResponseMidTask) else content_dict
        self.extract = self.content_dict.get("extract", "")
        self.questions = self.content_dict.get("questions", []) 
        self.answers = self.content_dict.get("answers", []) 
        if self.topic != self.content_dict.get("topic", ""):
            print(f"Warning: Topic mismatch between provided topic '{self.topic}' and content_dict topic '{self.content_dict.get('topic', '')}'")
        self.task_types = task_types
        self.section = "Middle_Task"
        
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
    
    def create_pdf(self, output_path=None, packet=None):
        # If packet is provided, append to existing PDF
        if packet:
            pdf_content = self._create_pdf(packet)
            return pdf_content
            
        if output_path is None:
            output_path = self.create_output_path()

        pdf_content = self._create_pdf()
        # Save PDF
        new_pdf = PdfReader(pdf_content)
        output_pdf = PdfWriter()
        output_pdf.add_page(new_pdf.pages[0])
        
        with open(output_path, "wb") as f:
            f.write(pdf_content.read())
        
        return output_path
        
        
    
    def _create_pdf(self, packet: BytesIO = None) -> BytesIO:
        print(f"Creating PDF for {self.task_types[0]} task...")
        
        if packet is None:
            self.create_pdf_initial()
        
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
        extract_y_position = y_start - line_height*3 - extract_height  # Starting position for extract
        extract_paragraph.drawOn(self.can, x_start, extract_y_position)
        
        # Calculate next position AFTER the extract
        # Get the actual height of the paragraph
        
        next_y_position = extract_y_position  # Add spacing
        
        # Draw headers (now positioned dynamically)
        next_y_position -= line_height * 2
        self.can.setFont("Helvetica-Bold", 12)
        self.can.drawString(x_start, next_y_position, "Intermediate Task 1")
        
        # Draw items
        next_y_position -= line_height * 3
        self.can.setFont("Helvetica", 12)
        self.can.drawString(x_start, next_y_position, "Determine whether the following statements are True or False based on the extract:")
        next_y_position -= line_height * 2
        for i, (question, answer) in enumerate(zip(self.questions, self.answers)):
            self.can.drawString(x_start, next_y_position, f"{i+1}. {question}")
            self.can.drawRightString(x_start + 180*mm, next_y_position, "True/False")
            next_y_position -= line_height
        
        # Draw Answers section
        # start a new page for the Answers section
        self.can.showPage()
        # redraw header on the new page
        can_width, can_height = A4
        self.can.setFont("Helvetica", 12)
        self.can.drawRightString(can_width - 20 * mm, 287 * mm, f"{self.skill}: {self.difficulty}")
        self.can.setFont("Helvetica", 18)
        self.can.drawRightString(can_width - 20 * mm, 280 * mm, self.topic)
        # reset vertical position for the new page
        next_y_position = y_start
        self.can.setFont("Helvetica-Bold", 16)
        next_y_position -= line_height * 8
        self.can.drawString(x_start, next_y_position, "Answers:")
        self.can.setFont("Helvetica", 12)
        next_y_position -= line_height * 2
        for answer in self.answers:
            self.can.drawString(x_start, next_y_position, f"{'True' if answer else 'False'}")
            next_y_position -= line_height

        # Save the canvas
        self.can.save()
        return self.packet
        
    pass

class Discussion(Task):
    def __init__(self, topic: str = None, content_dict: Union[ResponseDiscussion, dict] = None):
        """
        Initialize the Discussion task with the given parameters.
        Args:
            topic (str): The topic of the discussion
            content_dict (Union[ResponseDiscussion, dict], optional): Additional content for the task.
        """
        super().__init__(skill="Speaking", difficulty="A2", topic=topic, content_dict=content_dict)
        self.content_dict = content_dict.answer if isinstance(content_dict, ResponseDiscussion) else content_dict
        self.question = self.content_dict.get("question", "") if self.content_dict else ""
        self.section = "Discussion_Task"
    def create_pdf(self, output_path=None, packet=None):
        if packet:
            pdf_content = self.generate_pdf_content(packet)
            return pdf_content
            
        output_path = output_path if output_path else self.create_output_path()
        pdf_content = self.generate_pdf_content()
        # Save PDF
        new_pdf = PdfReader(pdf_content)
        output_pdf = PdfWriter()
        output_pdf.add_page(new_pdf.pages[0])
        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_content.read())
        return pdf_content
    
    def generate_pdf_content(self, packet: BytesIO = None):
        if packet:
            self.packet = packet
            
        # Positioning
        x_start = 20 * mm
        y_start = 270 * mm
        line_height = 5 * mm
        
        # Draw task title
        self.can.setFont("Helvetica-Bold", 16)
        self.can.drawString(x_start, y_start, "Discussion Task")
        
        # Draw instruction
        self.can.setFont("Helvetica", 12)
        instruction = f"Discuss the following question:"
        self.can.drawString(x_start, y_start - line_height*2, instruction)
        
        # Draw question
        self.can.setFont("Helvetica-Oblique", 12)
        self.can.drawString(x_start, y_start - line_height*4, self.question)
        
        # Save the canvas
        self.can.save()
        self.packet.seek(0)
        return self.packet

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
    
    {'topic': 'Asking for help', 'extract': "Dear Emily,\nI'm writing to ask for your help. I've been trying to fix my car but it's not working properly.\nCould you please recommend a reliable mechanic in your area? Also, if you have some time,\ncan you assist me with the repairs yourself? I'd really appreciate that because I'm\nnot very experienced with cars.\nI'll keep you updated on how things go. Let me know if you're available this weekend to work\non it together.\nBest regards,\nAlex", 'questions': ['The writer is asking for help with car repairs', 'Emily has experience in repairing cars', 'Alex knows an experienced mechanic', 'Alex plans to fix the car himself'], 'answers': [True, False, False, True]}
    
    middle_task_test = MiddleTask(
        skill = "Reading",
        difficulty = "A2", 
        topic = "An email from a friend",
        task_types = ["TF"], 
        content_dict = {
            "topic": "Asking for help",
            "extract": "Dear Emily,\nI'm writing to ask for your help. I've been trying to fix my car but it's not working properly.\nCould you please recommend a reliable mechanic in your area? Also, if you have some time,\ncan you assist me with the repairs yourself? I'd really appreciate that because I'm\nnot very experienced with cars.\nI'll keep you updated on how things go. Let me know if you're available this weekend to work\non it together.\nBest regards,\nAlex",
            "questions": [
                "The writer is asking for help with car repairs",
                "Emily has experience in repairing cars",
                "Alex knows an experienced mechanic",
                "Alex plans to fix the car himself"
            ],
            "answers": [True, False, False, True]
        }
    )

    output_path = middle_task_test.create_pdf()
    print("Created middle task PDF.")
    print(f"path at {output_path}")


    discussion_task_test = Discussion(
        topic="Planning a weekend trip",
        content_dict={
            "question": "What activities would you like to do on a weekend trip with friends?"
        }
    )
    output_path = discussion_task_test.create_pdf()
    print("Created discussion task PDF.")
    print(f"path at {output_path}")
