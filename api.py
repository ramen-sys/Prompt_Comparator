import os
from google import genai
from google.genai import types

import json

os.environ["GOOGLE_API_KEY"]="AIzaSyD3TJjXQu1nW-kOSrDcAb3U_-6f0HSW-nI"

client=genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

history=[]
if os.path.exists("history.json"):
    with open("history.json") as f:
        content=f.read().strip()
        if content:
            data=json.loads(content)
            history=[types.Content(role=m["role"],parts=[types.Part(text=m["text"])]) for m in data]

    

        




while True:
    user_input=input("User: ")
    if user_input.lower() in ["quit","end"]:
        break
    else:
        response=client.models.generate_content(model="gemini-2.5-flash",contents=history+[types.Content(role="user", parts=[types.Part(text=user_input)])],config= types.GenerateContentConfig(system_instruction="Always Keep the answer concise",temperature=0.7,max_output_tokens=1024))

        print(response.text)
        history.append(types.Content(role="user",parts=[types.Part(text=user_input)]))
        history.append(types.Content(role="model",parts=[types.Part(text=response.text)]))
        with open ("history.json",'w') as f:
            data=[{"role":m.role,"text":m.parts[0].text}for m in history]
            json.dump(data,f)
print("Ending chat")
