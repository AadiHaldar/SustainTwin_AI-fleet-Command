import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
    exit(1)
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

response = requests.get(url)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print("Available Models:")
    for model in data.get("models", []):
        print(f"- {model['name']}")
else:
    print(f"Error: {response.text}")
