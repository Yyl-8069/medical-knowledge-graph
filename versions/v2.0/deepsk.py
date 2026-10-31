import os
from openai import OpenAI

class DS_RedSpider():
    def __init__(self):
        self.client = OpenAI(api_key=os.environ['DEEPSEEK_API_KEY'], 
            base_url='https://api.deepseek.com/v1')
        
    def chat(self, prompt):
        response = self.client.chat.completions.create(
            model='deepseek-chat',
            # model="deepseek-reasoner",
            messages=[
            {"role": "system", "content": "你是⼀个⾮常专业且贴⼼的助⼿"},
            {"role": "user", "content": prompt},
                ],
            stream=False
            )
        
        return response.choices[0].message.content
