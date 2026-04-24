from datetime import datetime
import json
from dotenv import load_dotenv
import os
from openai import OpenAI
from server.data import DataManager
from server.sql import SQLManager
from server.log_formatter_factory import LogFormatterFactory, get_logger

load_dotenv()
api_key_loaded = os.getenv("API_KEY")
base_url_loaded = os.getenv("BASE_URL")
model_loaded = os.getenv("MODEL")
# 初始化客户端
client = OpenAI(
    api_key=api_key_loaded,
    base_url=base_url_loaded
)

class DeepSeekAPI:
    def __init__(self,dataManager: DataManager,sqlManager: SQLManager):
        self.dataManager = dataManager
        self.sqlManager = sqlManager
        # 这个要放在sql链接之后
        # 构建就全部写True吧
        for msg in self.dataManager.data.inner_conext:
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
        
    # 获取新的回复 输入的 text sender 一定是 me
    def fetch(self, text):
        # 使用工厂模式获取请求日志策略
        request_logger = get_logger('request')
        
        # 构建请求数据
        request_data = {
            "role": "user",
            "content": {
                "message": text,
                "send_time": str(datetime.now()),
                "should_reply": None
            }
        }
        
        # 记录请求日志（带截断）
        request_logger.log(request_data, prefix="API Request", max_length=300)
        
        self.dataManager.add_prompt({"role": "user", "content": f"""
                {{
                    "message": "{text}",
                    "send_time": "{datetime.now()}",
                    "should_reply": null
                }}
                """})
        
        # 更新两栈
        self.dataManager.add_inner_context("me", text)
        self.dataManager.add_display_context("me", text)
        # 更新数据库
        self.sqlManager.save_new("me", text)
        
        # 调用 API
        response = client.chat.completions.create(
            model=model_loaded,
            messages=self.dataManager.data.prompt,
            stream=False,
            temperature=0.8
        )
        
        # 使用工厂模式获取响应日志策略
        response_logger = get_logger('response')
        response_logger.log(response, prefix="API Response", max_length=500)

        # 解析返回的 json 串
        data = json.loads(response.choices[0].message.content)
        
        # 更新数据库
        return_content = data['message']
        should_reply = data['should_reply']
        self.sqlManager.save_new("ta", return_content)
        
        # 更新两栈
        self.dataManager.add_inner_context("ta", return_content)
        self.dataManager.add_display_context("ta", return_content)

        # 使用 API 日志策略记录返回内容
        api_logger = get_logger('api')
        api_logger.log({
            "message": return_content,
            "should_reply": should_reply
        }, prefix="API Return", max_length=200)

        return (True, return_content)