import os
from openai import OpenAI
from datetime import datetime
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_weather(location: str) -> str:
    # 这里需要替换为实际的天气API调用
    # 示例返回
    return f"{location}的天气晴朗，温度25℃，适合出行"

# 定义可用的工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

def execute_function(function_name: str, parameters: Dict[str, Any]) -> str:
    if function_name == "get_current_time":
        return get_current_time()
    elif function_name == "get_current_weather":
        return get_current_weather(parameters["location"])
    return "不支持的功能" 