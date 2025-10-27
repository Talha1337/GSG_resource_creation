"""
Simple GUI for generating British Council language learning resources.
Creates preparation tasks, middle tasks, and discussion sections combined into one PDF.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tasks import PreparationTask, MiddleTask, Discussion
from british_council_final_document import BritishCouncilFinalDocument
from running_ollama_easy import ResourceCreator
import threading

class GeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("British Council Resource Generator")
        self.root.geometry("500x300")
        
        # Variables
        self.topic_var = tk.StringVar()
        self.skill_var = tk.StringVar(value="Reading")
        self.difficulty_var = tk.StringVar(value="A1")
        self.output_name_var = tk.StringVar(value="final_document")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Resource Generator", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Topic input
        ttk.Label(main_frame, text="Topic:").grid(row=1, column=0, sticky=tk.W, pady=5)
        topic_entry = ttk.Entry(main_frame, textvariable=self.topic_var, width=40)
        topic_entry.grid(row=1, column=1, pady=5, padx=10, sticky=(tk.W, tk.E))
        
        # Skill selection
        ttk.Label(main_frame, text="Skill:").grid(row=2, column=0, sticky=tk.W, pady=5)
        skill_combo = ttk.Combobox(main_frame, textvariable=self.skill_var, 
                                  values=["Reading", "Writing", "Speaking", "Listening"], 
                                  state="readonly", width=37)
        skill_combo.grid(row=2, column=1, pady=5, padx=10, sticky=(tk.W, tk.E))
        
        # Difficulty selection
        ttk.Label(main_frame, text="Difficulty:").grid(row=3, column=0, sticky=tk.W, pady=5)
        difficulty_combo = ttk.Combobox(main_frame, textvariable=self.difficulty_var,
                                       values=["A1", "A2", "B1", "B2", "C1"],
                                       state="readonly", width=37)
        difficulty_combo.grid(row=3, column=1, pady=5, padx=10, sticky=(tk.W, tk.E))
        
        # Output filename
        ttk.Label(main_frame, text="Output Name:").grid(row=4, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_name_var, width=40)
        output_entry.grid(row=4, column=1, pady=5, padx=10, sticky=(tk.W, tk.E))
        
        # Generate button
        self.generate_button = ttk.Button(main_frame, text="Generate PDF", 
                                          command=self.start_generation)
        self.generate_button.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Progress label
        self.progress_label = ttk.Label(main_frame, text="", foreground="blue")
        self.progress_label.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def validate_inputs(self):
        """Validate user inputs."""
        if not self.topic_var.get().strip():
            messagebox.showerror("Error", "Please enter a topic name.")
            return False
        
        if not self.output_name_var.get().strip():
            messagebox.showerror("Error", "Please enter an output filename.")
            return False
        
        return True
    
    def generate_task(self):
        """Generate the PDF task in a separate thread to prevent UI freezing."""
        try:
            # Update progress
            self.progress_label.config(text="Initializing...")
            
            # Get user inputs
            topic = self.topic_var.get().strip()
            skill = self.skill_var.get()
            difficulty = self.difficulty_var.get()
            output_name = self.output_name_var.get().strip()
            
            # Add .pdf extension if not present
            if not output_name.endswith('.pdf'):
                output_name += '.pdf'
            
            # Create resource creator
            self.progress_label.config(text="Connecting to AI...")
            creator = ResourceCreator(topic=topic)
            
            # Create task objects
            self.progress_label.config(text="Creating preparation task...")
            preptask = PreparationTask(skill=skill, difficulty=difficulty, topic=topic)
            
            self.progress_label.config(text="Creating middle task...")
            midtask = MiddleTask(skill=skill, difficulty=difficulty, topic=topic, task_types=["tf"])
            
            self.progress_label.config(text="Creating discussion task...")
            discussion = Discussion(topic=topic)
            
            # Create final document
            self.progress_label.config(text="Generating final document...")
            example_doc = BritishCouncilFinalDocument(
                preparation_task=preptask,
                middle_task=midtask,
                discussion=discussion,
                creator=creator
            )
            
            # Generate PDF
            self.progress_label.config(text="Compiling PDF...")
            example_doc.generate_final_document(fp=output_name)
            
            # Success message
            self.progress_label.config(text="✓ PDF generated successfully!", foreground="green")
            messagebox.showinfo("Success", f"PDF generated successfully as '{output_name}'")
            
            # Reset button state
            self.generate_button.config(state="normal")
            
        except Exception as e:
            self.progress_label.config(text="✗ Error occurred", foreground="red")
            messagebox.showerror("Error", f"An error occurred while generating the PDF:\n{str(e)}")
            self.generate_button.config(state="normal")
    
    def start_generation(self):
        """Start the PDF generation process in a separate thread."""
        if not self.validate_inputs():
            return
        
        # Disable button to prevent multiple clicks
        self.generate_button.config(state="disabled")
        
        # Start generation in a separate thread
        thread = threading.Thread(target=self.generate_task, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = GeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

