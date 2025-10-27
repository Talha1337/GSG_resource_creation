from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel


class ResponsePrep(BaseModel):
  answer: dict

class ResponseMidTask(BaseModel):
  answer: dict
  
class ResponseMidTask2(BaseModel):
  topic: str
  extract : str
  questions: list[str]
  answers: list[bool]
  
class ResponseMidTaskQuestionsMCQ(BaseModel):
  """Response model for Multiple Choice questions in the middle task.

  Args:
      BaseModel (pydantic.BaseModel): Base model for data validation.
  """
  questions: list[str]
  options: list[list[str]]
  answers: list[str]
  
class ResponseMidTaskOrdering(BaseModel):
  """Response model for Ordering questions in the middle task.
  Args:
      BaseModel (pydantic.BaseModel): Base model for data validation.
  """
  
  items: list[str]
  correct_order: list[int]
  
class ResponseDiscussion(BaseModel):
  answer: dict
 
 
class ResourceCreator():
  def __init__(self, topic="A restaurant menu", model = "deepseek-r1:latest"):
    self.topic = topic
    self.difficulty = "A1"
    self.model = model

  def create_preparation_task(self) -> ResponsePrep:
    # This creates a ResponsePrep object which can be parsed to populate a PreparationTask
    response = chat(model=self.model, messages=[
      {
        'role': 'user',
        'content': f"""you are a helpful assistant that can help with creating preparation tasks for language learning materials.
        The preparation task should be a one-to-one matching task, matching words from two separate categories. The topic to create this preparation task on is: {self.topic}
        Provide as output a dictionary containing keys "labels", "correct_pairs". Return as JSON.
        
        EXAMPLE OUTPUT:
        {{
          "labels": ["Cities", "Countries"], 
          "correct_pairs": {{"Beijing": "China", "Buenos Aires": "Argentina", "Los Angeles": "The United States of America", "Amsterdam": "The Netherlands", "Mexico City": "Mexico", "Seoul": "The Republic of Korea", "Christchurch": "New Zealand", "Moscow": "Russia"}}
          }}
        
        """,
      },
        ],
        format = ResponsePrep.model_json_schema()
    )
    response_out = ResponsePrep.model_validate_json(response.message.content)
    return response_out.answer if response_out else None

  def create_middle_task(self) -> dict:
    response = chat(model=self.model, messages=[
      {
        'role': 'user',
        'content': f"""You are a helpful assistant that can help with creating extracts for English comprehension tasks, including relevant True/False questions.
        The extract should be approximately 100-150 words in length.
        The extract should be themed corresponding to the topic described. Questions should be based on the extract.
        The topic to create this extract on is: {self.topic}. Return as JSON.
        
        EXAMPLE OUTPUT:
          {{"topic": "An email from a friend",
          "extract": "Hi Samia,
          Quick email to say that sounds like a great idea. Saturday is better for me because I'm meeting my parents on Sunday. So if that's still good for you, why don't you come here? Then you can see the new flat and all the work we've done on the kitchen since we moved in. We can eat at home and then go for a walk in the afternoon. It's going to be so good to catch up finally. I want to hear all about your new job!
          Our address is 52 Charles Road, but it's a bit difficult to find because the house numbers are really strange here. If you turn left at the post office and keep going past the big white house on Charles Road, there's a small side street behind it with the houses 50–56 in. Don't ask me why the side street doesn't have a different name! But call me if you get lost and I'll come and get you.
          Let me know if there's anything you do/don't like to eat. Really looking forward to seeing you!
          See you soon!
          Gregor"
          "questions": [
          "Samia and Gregor are going to meet on Saturday",
          "They're going to have lunch at Gregor's flat",
          "They haven't seen each other for a long time",
          "Samia's life hasn't changed since they last met",
          "The house is easy to find",
          "Gregor doesn't know the name of the side street his flat is on",
          ],
          "answers": [True, True, True, False, False, False],
          }}
        """,
      },
        ],
        format = ResponseMidTask2.model_json_schema()
    )
    response_out = ResponseMidTask2.model_validate_json(response.message.content)
    
    # Convert ResponseMidTask2 to dictionary format compatible with existing content_dict structure
    if response_out:
      return {
        "topic": response_out.topic,
        "extract": response_out.extract,
        "questions": response_out.questions,
        "answers": response_out.answers
      }
    return None
  
  def create_middle_task_test2(self) -> ResponseMidTask2:
    response = chat(model=self.model, messages=[
      {
        'role': 'user',
        'content': f"""You are a helpful assistant that can help with creating extracts for English comprehension tasks, including relevant True/False questions.
        The extract should be approximately 100-150 words in length.
        The extract should be themed corresponding to the topic described. Questions should be based on the extract.
        The topic to create this extract on is: {self.topic}. Return as JSON.
        
        EXAMPLE OUTPUT:
          {{"topic": "An email from a friend",
          "extract": "Hi Samia,
          Quick email to say that sounds like a great idea. Saturday is better for me because I’m meeting my parents on Sunday. So if that’s still good for you, why don’t you come here? Then you can see the new flat and all the work we’ve done on the kitchen since we moved in. We can eat at home and then go for a walk in the afternoon. It’s going to be so good to catch up finally. I want to hear all about your new job!
          Our address is 52 Charles Road, but it’s a bit difficult to find because the house numbers are really strange here. If you turn left at the post office and keep going past the big white house on Charles Road, there’s a small side street behind it with the houses 50–56 in. Don’t ask me why the side street doesn’t have a different name! But call me if you get lost and I’ll come and get you.
          Let me know if there’s anything you do/don’t like to eat. Really looking forward to seeing you!
          See you soon!
          Gregor"
          "questions": [
          "Samia and Gregor are going to meet on Saturday",
          "They’re going to have lunch at Gregor’s flat",
          "They haven’t seen each other for a long time",
          "Samia’s life hasn’t changed since they last met",
          "The house is easy to find",
          "Gregor doesn’t know the name of the side street his flat is on",
          ],
          "answers": [True, True, True, False, False, False],
          }}
        """,
      },
        ],
        format = ResponseMidTask2.model_json_schema()
    )
    response_out = ResponseMidTask2.model_validate_json(response.message.content)
    return response_out.answer if response_out else None

  def create_discussion(self) -> ResponseDiscussion:
    response = chat(model=self.model, messages=[
      {
        'role': 'user',
        'content': f"""You are a helpful assistant that can help with creating discussion prompts for English comprehension tasks.
        The discussion prompt should consist of a single question.
        The discussion prompt should be related to the topic specified.
        The topic to create this discussion prompt on is {self.topic}. Return as JSON.
        
        EXAMPLE OUTPUT:
        {{
          "topic": "An international departures board"
          "question": "How often do you travel by plane? Which countries would you like to visit?"
          }}
        
        """,
      },
        ],
        format = ResponseDiscussion.model_json_schema()
    )
    response_out = ResponseDiscussion.model_validate_json(response.message.content)
    return response_out.answer if response_out else None
# This is where the topic name would go. "The topic to create ... "


if __name__ == "__main__":
  # res_creator = ResourceCreator(topic="A restaurant menu", model = "deepseek-r1:latest")
  # print(res_creator.create_preparation_task().answer)
  res_creator_2 = ResourceCreator(topic="Asking for help", model = "deepseek-r1:latest")
  print(res_creator_2.create_middle_task().answer)