from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel

class Response(BaseModel):
    answer: dict
# This is where the topic name would go. "The topic to create ... "
response = ChatResponse = chat(model='tinyllama', messages=[
  {
    'role': 'user',
    'content': f"""you are a helpful assistant that can help with creating preparation tasks for language learning materials.
    The preparation task should be a one-to-one matching task, matching words from two separate categories. The topic to create this preparation task on is: An airline departures board.
    Provide as output a dictionary containing keys "cat1", "cat2", "correct_pairs", 
    """,
  },
    ],
    format = Response.model_json_schema()
)


response_out = Response.model_validate_json(response.message.content)
print(response_out.answer)