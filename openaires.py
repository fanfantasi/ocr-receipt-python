import os
from dotenv import load_dotenv
import base64
import openai
import json
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAiRes():

    def __init__(self, raw, keyword):
        self.raw = raw
        self.keyword = keyword
        try:
            self.res = openai.Completion.create(model="text-davinci-003", prompt= "Extract {} to json: {} ".format(keyword, raw), temperature=0, max_tokens=500, top_p=1, frequency_penalty=0, presence_penalty=0)
        except TypeError:
            raise Exception("Could not decode base64 data")

    def get_datares(self):
        return self.res.choices[0].text