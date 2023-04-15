from time import sleep
import requests

class BerriAI:
    def __init__(self):
        self.api_endpoint = None

    def get_api_endpoint(self):
        url = "https://api.berri.ai/create_app"
        data = {"user_email": "krrish@berri.ai"}
        files = {'data_source': open('input.pdf', 'rb')}

        response = requests.post(url, files=files, data=data)
        print(response.text)

        self.api_endpoint = response.json()["api_endpoint"]
        return self.api_endpoint

    def query_api_endpoint(self, user_query):
        if not self.api_endpoint:
            raise ValueError("API endpoint not set. Please call get_api_endpoint() first.")

        final_url = self.api_endpoint + "&query=" + user_query
        response = requests.get(final_url)

        print(response.text)
        system_response = response.json()["response"]
        return system_response

if __name__ == "__main__":
    berri = BerriAI()
    api_endpoint = berri.get_api_endpoint()
    sleep(3)
    user_query = "do you know about berri.ai?"
    system_response = berri.query_api_endpoint(user_query)
    print(f"System response: {system_response}")


# {
#     "account_email": "krrish@berri.ai",
#     "api_endpoint": "https://api.berri.ai/query?user_email=krrish@berri.ai&instance_id=51ecdb70-bfa2-4ceb-a817-9b2bcc13eab7",
#     "instance_id": "51ecdb70-bfa2-4ceb-a817-9b2bcc13eab7",
#     "playground_endpoint": "play.berri.ai/aHR0cHM6Ly9zdG9yZXF1ZXJ5YWJoaTItYXlsdS56ZWV0LWJlcnJpLnplZXQuYXBwL2JlcnJpX3F1ZXJ5P3Byb2pfcGF0aD1pbmRleGVzL2tycmlzaEBiZXJyaS5haS81MWVjZGI3MC1iZmEyLTRjZWItYTgxNy05YjJiY2MxM2VhYjcmcHJval9uYW1lPVN0cmF3YmVycnkgUHJvamVjdCZxdWVyeT0=",
#     "website_endpoint": "chat.berri.ai/aHR0cHM6Ly9zdG9yZXF1ZXJ5YWJoaTItYXlsdS56ZWV0LWJlcnJpLnplZXQuYXBwL2JlcnJpX3F1ZXJ5P3Byb2pfcGF0aD1pbmRleGVzL2tycmlzaEBiZXJyaS5haS81MWVjZGI3MC1iZmEyLTRjZWItYTgxNy05YjJiY2MxM2VhYjcmcHJval9uYW1lPVN0cmF3YmVycnkgUHJvamVjdCZxdWVyeT0="
# }
