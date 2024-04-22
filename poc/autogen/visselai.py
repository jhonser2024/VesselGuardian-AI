from typing import Optional, Type
from langchain_community.chat_models import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain.tools.file_management.read import ReadFileTool
import autogen
import gradio as gr

# 1. Create Circumference Tool
class SaludadorToolInput(BaseModel):
    mensaje: str = Field()

class SaludadorTool(BaseTool):
    name = "greenting"
    description = "Usa esta herramienta cuando necesites saludar"
    args_schema: Type[BaseModel] = SaludadorToolInput

    def _run(self, mensaje: str):
        return f"Hola como estas y tales de tales ,{mensaje}"

def generate_llm_config(tool):
    function_schema = {
        "name": tool.name.lower().replace(" ", "_"),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    if tool.args is not None:
        function_schema["parameters"]["properties"] = tool.args

    return function_schema

custom_tool = SaludadorTool()

def run_assistant(message):
    llm_configlocal =[ {"model": "gpt-4-turbo-2024-04-09", "api_key": "xxxxxxxxxxxxxxx"}]


    llm_config = {
    "functions": [
        generate_llm_config(custom_tool)
    ],
    "config_list": llm_configlocal,
    "timeout": 120,
    }

    # 4. Creating User Agent and Registering Tools
    user = autogen.UserProxyAgent(
    name="user",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },
    )

    user.register_function(
    function_map={
        custom_tool.name: custom_tool._run
    }
    )

    # 5. Create Circumference Agent and Initiate Chat
    agent = autogen.AssistantAgent(
    name="Agente saludador",
    system_message="Para las tareas de codificación, utiliza solo las funciones que te hayan sido proporcionadas. Responde TERMINATE cuando la tarea esté completada.",
    llm_config=llm_config,
    )

    response = user.initiate_chat(
    agent,
    message= message,
    llm_config=llm_config,
    summary_method="reflection_with_llm",
    )
    return response

iface = gr.Interface(fn=run_assistant,inputs="text",outputs="text",title="Llama2")
iface.launch()