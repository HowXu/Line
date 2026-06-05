from datetime import datetime
import json
from dotenv import load_dotenv
import os
from openai import OpenAI
from server.data import DataManager
from server.sql import SQLManager
from server.log_formatter_factory import LogFormatterFactory, get_logger, get_creator
from server.log_strategy import LogContext

load_dotenv()
api_key_loaded = os.getenv("API_KEY")
base_url_loaded = os.getenv("BASE_URL")
model_loaded = os.getenv("MODEL")

# 初始化客户端
client = OpenAI(
    api_key=api_key_loaded,
    base_url=base_url_loaded,
)


class DeepSeekAPI:
    """
    业务门面：组合数据管理、SQL 持久化与日志策略。

    内部使用 LogContext（策略模式的 Context）来切换不同日志族：
        request_log   -> RequestLogStrategy
        response_log  -> ResponseLogStrategy
        api_log       -> APILogStrategy
    LogContext 通过 LogStrategyCreator 间接获取具体策略，呈现工厂方法结构。
    """

    def __init__(self, dataManager: DataManager, sqlManager: SQLManager):
        self.dataManager = dataManager
        self.sqlManager = sqlManager

        # 把历史消息注入 prompt（略，与原实现一致）
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

        # 策略模式 Context：使用工厂方法创建 Creator，并组装 LogContext
        self.request_log = LogContext(get_creator("request"))
        self.response_log = LogContext(get_creator("response"))
        self.api_log = LogContext(get_creator("api"))

    def fetch(self, text):
        # ---------- 请求阶段 ----------
        request_data = {
            "role": "user",
            "content": {
                "message": text,
                "send_time": str(datetime.now()),
                "should_reply": None,
            },
        }
        self.request_log.write(request_data, prefix="API Request", max_length=300)

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

        # ---------- 调用 API ----------
        response = client.chat.completions.create(
            model=model_loaded,
            messages=self.dataManager.data.prompt,
            stream=False,
            temperature=0.8,
        )

        # ---------- 响应阶段 ----------
        self.response_log.write(response, prefix="API Response", max_length=500)

        # 解析返回的 json 串
        data = json.loads(response.choices[0].message.content)

        # 更新数据库
        return_content = data["message"]
        should_reply = data["should_reply"]
        self.sqlManager.save_new("ta", return_content)

        # 更新两栈
        self.dataManager.add_inner_context("ta", return_content)
        self.dataManager.add_display_context("ta", return_content)

        # ---------- API 摘要阶段 ----------
        self.api_log.write(
            {"message": return_content, "should_reply": should_reply},
            prefix="API Return",
            max_length=200,
        )

        return (True, return_content)
