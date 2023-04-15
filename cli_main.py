import subprocess
from termcolor import colored
import json
import os
import openai
import sys
import dotenv
dotenv.load_dotenv()

MODEL = 'gpt-3.5-turbo'

# Authenticate with the OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

class ActionProcessor:
    def __init__(self, actions):
        self.actions = actions

    def process_actions(self):
        for action in self.actions:
            if action['action'] == 'create_file':
                self.create_file(action['payload']['filename'], action['payload']['filecontent'])
            elif action['action'] == 'run_shell_command':
                self.run_shell_command(action['payload']['command'])

    def create_file(self, filename, filecontent):
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filename, 'w') as file:
            file.write(filecontent)

    def run_shell_command(self, command):
        subprocess.run(command, shell=True, check=True)


def chatgpt_query(messages):
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
        )
        return response.choices[0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        print(f"Error: {e}")
        sys.exit(1)

def read_files_in_folder(folder_path):
    file_content_dict = {}

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        # Check if the path is a file and not a directory
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                file_content = file.read()
                file_content_dict[file_name] = file_content

    return file_content_dict

def template_user_input(user_input):
    additional_info = read_files_in_folder("./cli_templates")

    template_id = user_input.split(" ")[1]
    templates = {
        "json_response": "Generate a JSON string with action 'create_file' and a payload containing file content and file name. JSON string only. Nothing else",

        "create_flask_app": """
            For the next response, please respond in a JSON string.

            The JSON format should be:
            [
                {action:"create_file", payload: {filename:'', filecontent:}},
                {action:"run_shell_command", payload: {command: "./venv/bin/pip install"}}
            ]

            JSON strings must not have unescaped line breaks. 
            Please use triple-quotes for multiline strings in Python and escape any double-quotes inside the string.

            the question is: please create a web app with flask and html

            it should have one page, 
            - /  returns a html page. The html page should say "hello world"
        """,
        
        "create_berri_app": """
            For the next response, please respond in a JSON string.

            The JSON format should be:
            [
                {action:"create_file", payload: {filename:'', filecontent:}},
                {action:"run_shell_command", payload: {command: "./venv/bin/pip install"}}
            ]

            JSON strings must not have unescaped line breaks. 
            Please use triple-quotes for multiline strings in Python and escape any double-quotes inside the string.

            the question is: please create a web app with flask and html

            it should have several pages, 
            - / should redirect to /upload
            - /upload should have a form with a file input and a submit button. Upon submit, it should redirect to /ask
            - /ask should have a form with a text input and a submit button. Upon submit, it should redirect to /result
            - app.py should have __name__ == "__main__" and run the app
            
            The /upload html page should:
            - allow the user to upload a PDF file. The server will save it as input.pdf.

            All html should under /templates directory

            Inside the /ask endpoint, the server will:
            - send the PDF file to berri.ai
            - send the question to berri.ai
            - return the result back to the user
            - please keep the PDF file in the server

            Please see below on how to interact with berri.ai
        """ + additional_info.get('berri.py'),
    }
    return templates.get(template_id, "Template not found.")

def process_response_json(response_json):
    if isinstance(response_json, dict):
        print("The response_json is a dictionary.")

        action = response_json.get("action", "")
        payload = response_json.get("payload", {})

        if action == "create_file":
            file_content = payload.get("file_content", "")
            file_name = payload.get("file_name", "output.txt")

            with open(file_name, "w") as output_file:
                output_file.write(file_content)

            print(f"File '{file_name}' created with content:\n{file_content}")

    elif isinstance(response_json, list):
        print("The response_json is a list (array).")
        processor = ActionProcessor(response_json)
        processor.process_actions()

    else:
        print("The instance is neither a dictionary nor a list (array).")



def main():
    print("Welcome to the ChatGPT CLI Client! Type 'exit' to quit.")

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    while True:
        user_input = input(colored("You: ", "blue"))
        if user_input.lower() == 'exit':
            break

        if user_input.lower().startswith("/template "):
            templated_user_input = template_user_input(user_input)
            messages.append({"role": "user", "content": templated_user_input})
            print(colored(f"You: ", "blue"), templated_user_input)
        else:
            messages.append({"role": "user", "content": user_input})

        assistant_response = chatgpt_query(messages)
        messages.append({"role": "assistant", "content": assistant_response})
        print(colored(f"ChatGPT: {assistant_response}", "green"))

        try:
            response_json = json.loads(assistant_response)
            process_response_json(response_json)
        except json.JSONDecodeError:
            print("ChatGPT response is not a valid JSON.")
            pass

if __name__ == '__main__':
    main()
