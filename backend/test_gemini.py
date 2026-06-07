import requests
import os

api_key = "AQ.Ab8RN6JEMAj1CVh0qMetYUKn71MBbnD6ENnL9V38wKOeS0Or8g"
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
