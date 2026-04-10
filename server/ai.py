from datetime import datetime
import json

from openai import OpenAI

from server.data import DataManager
from server.sql import SQLManager

# 初始化客户端
client = OpenAI(
    api_key="sk-c18d6e09e8f14a84849e6597b42e8c01",
    base_url="https://api.deepseek.com"
)

class DeepSeekAPI:
    def __init__(self,dataManager: DataManager,sqlManager: SQLManager):
        self.dataManager = dataManager
        self.sqlManager = sqlManager
        # 这个要放在sql链接之后
        # 构建就全部写True吧
        for msg in self.dataManager.inner_conext:
            if msg["sender"] == "me":
                self.dataManager.add_prompt({"role": "user", "content": f"""
                {{
                    "message": "{msg['text']}",
                    "send_time": "{msg['time']}",
                    "should_reply": null
                }}
                """})
            else:
                self.dataManager.add_prompt({"role": "assistant", "content": f"""
                {{
                    "message": "{msg['text']}",
                    "send_time": "{msg['time']}",
                    "should_reply": null
                }}
                """})
        
    # 获取新的回复 输入的text sender一定是me
    def fetch(self, text):
        self.dataManager.add_prompt({"role": "user", "content": f"""
                {{
                    "message": "{text}",
                    "send_time": "{datetime.now()}",
                    "should_reply": null
                }}
                """})
        print(self.dataManager.prompt)
        # 更新两栈
        self.dataManager.add_inner_context("me",text)
        self.dataManager.add_display_context("me",text)
        # 更新数据库
        self.sqlManager.save_new("me",text)
        # 调用API
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=self.dataManager.prompt,
            stream=False,
            temperature=0.8
        )
        print(response)
        # 解析返回的json串
        data = data = json.loads(response.choices[0].message.content)
        # 更新数据库
        return_content = data['message']
        should_reply = data['should_reply']
        self.sqlManager.save_new("ta",return_content)
        # 更新两栈
        self.dataManager.add_inner_context("ta",return_content)
        self.dataManager.add_display_context("ta",return_content)

        return (True,return_content)