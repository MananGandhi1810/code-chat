import google.generativeai as genai
import dotenv
import os
from zipfile import ZipFile
import requests
import io


dotenv.load_dotenv()


def read_zip(url: str) -> dict:
    response = requests.get(
        url,
        headers={
            "User-Agent": "request",
            "Accept": "application/vnd.github+json",
        },
    )
    zip = ZipFile(io.BytesIO(response.content))
    file_tree = []
    for file in zip.namelist():
        if file.endswith("/"):
            continue
        try:
            contents = zip.open(file, "r").read().decode()
            file_tree.append(f"\n---{file}---\n{contents}")
        except UnicodeDecodeError:
            pass
    return file_tree


repo = "MananGandhi1810/online-ide"

contents = read_zip(f"https://api.github.com/repos/{repo}/zipball")
str_contents = "\n".join(contents)

model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=f"""
You are a copilot who helps the user with code related questions.
Do not answer about anything that is not related to the code given below.
Follow code best-practices, and help the user get the best results out of their code.
The following is the full codebase that the user is working in:
{str_contents}
You have full access to the entire codebase, there are no files outside it and apart from those mentioned in gitignore.
Always give an answer with everything you think is correct, do not hesitate to answer
If you are generating code, do not give any comments asking the user to continue, such as `// Add more tests`
Only provide code in the language that the user is using, no other languages. Also, do not use typescript if the main language in the codebase is javascript
All questions should be answered comprehensively with details, unless the user requests a concise response specifically
""",
)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
chat = model.start_chat(history=[])

while True:
    user_message = input("> ")
    if user_message.lower() == "exit":
        break
    response = chat.send_message(user_message, stream=True)
    for chunk in response:
        print(chunk.text, end="")
