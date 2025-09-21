"""
Will take as input a PreprationTask object, a list of Task objects, (ideally length 2 but can vary), 
and a Discussion object. It will then generate a final document that is a pdf with the sections based on
the objects provided.
"""
from preparation_task import PreparationTask
from task import Task
from discussion import Discussion
from typing import List

class BritishCouncilFinalDocument:
    def __init__(self, preparation_task : PreparationTask, tasks : List[Task], discussion : Discussion):
        self.initial_document = None
        self.preparation_task = preparation_task
        self.tasks = tasks
        self.discussion = discussion

    def generate_final_document(self, fp : str = "final_document.pdf") -> bool:
        """
        Will generate a final document that is a pdf with the sections based on
        the objects provided.
        Saves the document to the current working directory.
        Returns True if the document is generated successfully, False otherwise.
        """
        pass

    def _generate_preparation_task_section(self) -> str:
        """
        Will generate a section for the preparation task.
        """
        pass
    
    def _generate_tasks_section(self) -> str:
        """
        Will generate a section for the tasks.
        """
        pass
    
    def _generate_discussion_section(self) -> str:
        """
        Will generate a section for the discussion.
        """
        pass

