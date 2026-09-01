import os, requests, json
from dotenv import load_dotenv
load_dotenv('backend/.env')
url = 'https://api.groq.com/openai/v1/chat/completions'
headers = {'Authorization': f'Bearer {os.getenv("GROQ_API_KEY")}', 'Content-Type': 'application/json'}
payload = {'model': 'openai/gpt-oss-20b', 'messages': [{'role': 'user', 'content': 'hello'}], "response_format": {"type": "json_object"}}
print(requests.post(url, headers=headers, json=payload).json())
