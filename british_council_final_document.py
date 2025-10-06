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
        self.pdf_content = BytesIO()
        self.preparation_task = preparation_task
        self.middle_task = middle_task
        self.discussion = discussion
        self.creator = creator
        if self.creator is None:
                self.creator = ResourceCreator(topic=self.preparation_task.topic)
    def generate_final_document(self, fp : str = "final_document.pdf") -> bool:
        """
        Will generate a final document that is a pdf with the sections based on
        the objects provided.
        Saves the document to the current working directory.
        Returns True if the document is generated successfully, False otherwise.
        """
        pass

    def _generate_preparation_task_section(self) -> BytesIO:
        """
        Will generate a section for the preparation task.
        """
        print("Generating preparation task section...")
        self.pdf_content = self.preparation_task._create_matching_task_pdf(self.pdf_content)
    
    def _generate_tasks_section(self) -> str:
        """
        Will generate a section for the tasks.
        """
        self.middle_task.create_task_pdf()
    
    def _generate_discussion_section(self) -> str:
        """
        Will generate a section for the discussion.
        """
        pass
    
    def save_document(self, fp : str = "final_document.pdf") -> bool:
        """
        Saves the document to the current working directory.
        Returns True if the document is saved successfully, False otherwise.
        """
        # Save PDF
        print("saving document...")
        try:
            new_pdf = PdfReader(self.pdf_content)
            output_pdf = PdfWriter()
            for page in new_pdf.pages:
                output_pdf.add_page(page)
            
            with open(fp, "wb") as f:
                output_pdf.write(f)
            print(f"Document saved successfully as {fp}")
            return True
        except Exception as e:
            print(f"Error saving document: {e}")
            return False
    

if __name__ == "__main__":
    
    prep_task = PreparationTask(
        skill="Speaking",
        difficulty="A2",
        topic="Travel",
        correct_pairs={
            "airport": "a place where planes take off and land",
            "luggage": "bags and suitcases",
            "boarding pass": "a document that allows you to get on a plane"
        }
    ),
    example_doc = BritishCouncilFinalDocument(
        prep_task,
        ,
        None
    )

    example_doc._generate_preparation_task_section()
    example_doc.save_document("example_final_document.pdf")
