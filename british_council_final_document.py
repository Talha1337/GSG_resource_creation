"""
Will take as input a PreprationTask object, a list of Task objects, (ideally length 2 but can vary), 
and a Discussion object. It will then generate a final document that is a pdf with the sections based on
the objects provided.
"""
from tasks import PreparationTask, MiddleTask, Discussion
from PyPDF2 import PdfReader, PdfWriter
import os
from typing import List
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from running_ollama_easy import ResourceCreator

class BritishCouncilFinalDocument:
    def __init__(self, preparation_task : PreparationTask, middle_task : MiddleTask, discussion : Discussion, creator : ResourceCreator = None):
        """
        Initialize the final document generator.
        """
        self.preparation_task = preparation_task
        self.middle_task = middle_task
        self.discussion = discussion
        self.creator = creator
        self.task_pdfs = []  # Store PDF buffers for each task section
        if self.creator is None:
            print("WARNING: No creator specified. Creator is needed for generation.")
            
    def generate_final_document(self, fp : str = "final_document.pdf") -> bool:
        """
        Will generate a final document that is a pdf with the sections based on
        the objects provided.
        Saves the document to the current working directory.
        Returns True if the document is generated successfully, False otherwise.
        """
        print("Generating final document...")
        print("Generating preparation task section...")
        self._generate_preparation_task_section()
        print("Generating tasks section...")
        self._generate_tasks_section()
        print("Generating discussion section...")
        self._generate_discussion_section()
        self.save_document(fp)
        return True

    def _generate_preparation_task_section(self):
        """
        Will generate a section for the preparation task.
        """
        print("Generating preparation task section...")
        if not self.preparation_task or self.preparation_task.content_dict == None:
            print("No preparation task content provided.")
            print("We will attempt to generate it now...")
            self.preparation_task.content_dict = self.creator.create_preparation_task()
            print("--PREPARATION TASK CREATED--")
            print(self.preparation_task.content_dict)
            print("--PREPARATION TASK CREATED--")
        # Create PDF for preparation task
        prep_pdf = self.preparation_task._create_matching_task_pdf()
        prep_pdf.seek(0)
        self.task_pdfs.append(prep_pdf)
    
    def _generate_tasks_section(self):
        """
        Will generate a section for the tasks.
        """
        if self.middle_task.content_dict == None:
            print("No middle task content provided.")
            print("We will attempt to generate it now...")
            self.middle_task.content_dict = self.creator.create_middle_task()
        
        # Create PDF for middle task
        mid_pdf = self.middle_task._create_pdf()
        mid_pdf.seek(0)
        self.task_pdfs.append(mid_pdf)
    
    def _generate_discussion_section(self):
        """
        Will generate a section for the discussion.
        """
        if self.discussion.content_dict == None:
            print("No discussion content provided.")
            print("We will attempt to generate it now...")
            self.discussion.content_dict = self.creator.create_discussion()
            print("--CONTENT DICTIONARY--")
            print(self.discussion.content_dict)
            print("--CONTENT DICTIONARY--")
        # Create PDF for discussion
        disc_pdf = self.discussion.generate_pdf_content()
        disc_pdf.seek(0)
        self.task_pdfs.append(disc_pdf)
    
    def save_document(self, fp : str = "final_document.pdf") -> bool:
        """
        Saves the document to the current working directory.
        Combines all task PDFs into a single document.
        Returns True if the document is saved successfully, False otherwise.
        """
        print("Merging all sections into final document...")
        try:
            output_pdf = PdfWriter()
            
            # Merge all PDFs
            for i, task_pdf in enumerate(self.task_pdfs):
                try:
                    pdf_reader = PdfReader(task_pdf)
                    print(f"Adding section {i+1} with {len(pdf_reader.pages)} page(s)...")
                    for page in pdf_reader.pages:
                        output_pdf.add_page(page)
                except Exception as e:
                    print(f"Error processing section {i+1}: {e}")
                    continue
            
            # Save the combined PDF
            with open(fp, "wb") as f:
                output_pdf.write(f)
            print(f"Final document saved successfully as {fp}")
            return True
        except Exception as e:
            print(f"Error saving document: {e}")
            return False
    

if __name__ == "__main__":
    
    content_dict = {
    "topic": "An airport departures board",
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
    
    topic_name = "Asking for help"
    # preptask = PreparationTask(skill = "Speaking", difficulty = "A1", topic = topic_name, content_dict = content_dict)
    # midtask = MiddleTask(skill = "Speaking", difficulty = "A1", topic = topic_name, task_types = ["tf"],
    #                      content_dict  = {
    #                     "topic": "Asking for help",
    #                     "extract": "Dear Emily,\nI'm writing to ask for your help. I've been trying to fix my car but it's not working properly.\nCould you please recommend a reliable mechanic in your area? Also, if you have some time,\ncan you assist me with the repairs yourself? I'd really appreciate that because I'm\nnot very experienced with cars.\nI'll keep you updated on how things go. Let me know if you're available this weekend to work\non it together.\nBest regards,\nAlex",
    #                     "questions": [
    #                         "The writer is asking for help with car repairs",
    #                         "Emily has experience in repairing cars",
    #                         "Alex knows an experienced mechanic",
    #                         "Alex plans to fix the car himself"
    #                     ],
    #                     "answers": [True, False, False, True]})
    # discussion = Discussion(topic = topic_name, content_dict = {"question": "What activities would you like to do on a weekend trip with friends?"})
    # Testing automatic generation of content
    preptask = PreparationTask(skill = "Speaking", difficulty = "A1", topic = topic_name)
    midtask = MiddleTask(skill = "Speaking", difficulty = "A1", topic = topic_name, task_types = ["tf"])
    discussion = Discussion(topic = topic_name)
    example_doc = BritishCouncilFinalDocument(
        preparation_task = preptask,
        middle_task = midtask,
        discussion = discussion,
        creator = ResourceCreator(topic=topic_name)
    )

    example_doc.generate_final_document(fp = "example_final_document.pdf")