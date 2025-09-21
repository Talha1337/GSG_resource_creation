from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from io import BytesIO
import os
import random

class Task:
    def __init__(self, skill, difficulty, topic, correct_pairs):
        """
        Parent class to create different types of tasks for language learning materials.
        
        Args:
            skill (str): The language skill (e.g., "Reading", "Writing", "Speaking", "Listening")
            difficulty (str): The difficulty level (e.g., "A1", "A2", "B1", "B2", "C1")
            topic (str): The topic of the exercise
            correct_pairs (dict): Dictionary of correct answer pairs (e.g., {"item1": "answer1"})
            task_type (str): Type of task (default: "matching")
        """
        self.skill = skill
        self.difficulty = difficulty
        self.topic = topic
        self.correct_pairs = correct_pairs
        self.answer_key = {}
    pass

class PreparationTask(Task):
    """
    A class to create preparation tasks for language learning materials.
    Supports matching exercises with customizable content and formatting.
    """
    
    def __init__(self, skill, difficulty, topic, correct_pairs, task_type="matching"):
        """
        Initialize a PreparationTask.
        
        Args:
            skill (str): The language skill (e.g., "Reading", "Writing", "Speaking", "Listening")
            difficulty (str): The difficulty level (e.g., "A1", "A2", "B1", "B2", "C1")
            topic (str): The topic of the exercise
            correct_pairs (dict): Dictionary of correct answer pairs (e.g., {"item1": "answer1"})
            task_type (str): Type of task (default: "matching")
        """
        super().__init__(skill, difficulty, topic, correct_pairs)
        if task_type != "matching":
            raise ValueError("Currently, only 'matching' task type is supported")
        
    def _shuffle_answers(self):
        """
        Shuffle the answers to create variation in correct answer patterns.
        
        Returns:
            tuple: (shuffled_items, shuffled_answers, answer_key)
        """
        items = list(self.correct_pairs.keys())
        answers = list(self.correct_pairs.values())
        
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
        packet = BytesIO() if None else packet
        can = canvas.Canvas(packet, pagesize=A4)
        can_width = A4[0]
        
        # Add header information
        can.setFont("Helvetica", 12)
        can.drawRightString(can_width - 20 * mm, 287 * mm, f"{self.skill}: {self.difficulty}")
        can.setFont("Helvetica", 18)
        can.drawRightString(can_width - 20 * mm, 280 * mm, self.topic)
        
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
        can.setFont("Helvetica-Bold", 16)
        can.drawString(x_start, y_start, "Preparation task")
        
        # Draw instruction
        can.setFont("Helvetica", 12)
        instruction = f"Match the items (1–{len(items)}) with the answers (a–{chr(96+len(items))})."
        can.drawString(x_start, y_start - line_height*2, instruction)
        
        # Draw headers
        can.setFont("Helvetica-Bold", 12)
        can.drawString(x_start, y_start - 4 * line_height, "Items")
        can.drawString(x_answers, y_start - 4 * line_height, "Answers")
        
        # Draw items and answers
        can.setFont("Helvetica", 12)
        for i in range(len(items)):
            can.drawString(x_start, y_start - (5 + i) * line_height, items_formatted[i])
            can.drawString(x_answers, y_start - (5 + i) * line_height, answers_formatted[i])
        
        # Add answers section
        self._add_answers_section(can, x_start, y_start, line_height, len(items))
        
        can.save()
        packet.seek(0)
        return packet
    
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
            # Create default filename based on skill, difficulty, and topic
            safe_topic = self.topic.replace(" ", "_").replace("-", "_")
            filename = f"{self.skill}_{self.difficulty}_{safe_topic}_Preparation_Task.pdf"
            current_dir = os.getcwd()
            output_path = os.path.join(current_dir, "resources_edited", "Reading", filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF content
        if self.task_type == "matching":
            pdf_content = self._create_matching_task_pdf()
        else:
            raise ValueError(f"Task type '{self.task_type}' not supported yet")
        
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
    """
    pass

class Discussion(Task):
    pass

# Example usage
if __name__ == "__main__":
    # Define the correct city and country pairs
    correct_pairs = {
        "Beijing": "China",
        "Buenos Aires": "Argentina", 
        "Los Angeles": "The United States of America",
        "Amsterdam": "The Netherlands",
        "Mexico City": "Mexico",
        "Seoul": "The Republic of Korea",
        "Christchurch": "New Zealand",
        "Moscow": "Russia"
    }
    
    # Create a preparation task
    task = PreparationTask(
        skill="Reading",
        difficulty="A1",
        topic="An airport departures board",
        correct_pairs=correct_pairs
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
        correct_pairs={"CEO": "Chief Executive Officer", "HR": "Human Resources"}
    )

    # Create the PDF
    output_path = vocabulary_task.create_pdf()
    print(f"Answer key: {vocabulary_task.get_answer_key()}")
