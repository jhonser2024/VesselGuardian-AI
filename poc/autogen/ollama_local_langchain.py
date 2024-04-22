import math
import os
from typing import Optional, Type
from langchain_community.chat_models import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain.tools.file_management.read import ReadFileTool
import autogen

# 1. Create Circumference Tool
class CircumferenceToolInput(BaseModel):
    radius: float = Field()

class CircumferenceTool(BaseTool):
    name = "circumference_calculator"
    description = "Use this tool when you need to calculate a circumference using the radius of a circle"
    args_schema: Type[BaseModel] = CircumferenceToolInput

    def _run(self, radius: float):
        return float(radius) * 2.0 * math.pi

# 2. Get File Path for radius file (Used by Inbuilt ReadFileTool)
def get_file_path_radius():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "radius.txt")
    return file_path

# 3. LLM Config 
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


# Instantiate the ReadFileTool
read_file_tool = ReadFileTool()
custom_tool = CircumferenceTool()

# Construct the llm_config

local_llm_config = [
    {
            "model": "NotRequired", # Loaded with LiteLLM command
            "api_key": "NotRequired", # Not needed
            "base_url": "http://0.0.0.0:4000"  # Your LiteLLM URL
    }
    ]


llm_config = {
    "functions": [
        generate_llm_config(custom_tool),
        generate_llm_config(read_file_tool),
    ],
    "config_list": local_llm_config,
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
        custom_tool.name: custom_tool._run,
        read_file_tool.name: read_file_tool._run,
    }
)

# 5. Create Circumference Agent and Initiate Chat
CircumferenceAgent = autogen.AssistantAgent(
    name="Circumference Agent",
    system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
)

user.initiate_chat(
    CircumferenceAgent,
    message=f"Read the file with the path {get_file_path_radius()}, then calculate the circumference of a circle that has a radius of that files contents.",  # 7.81mm in the file
    llm_config=llm_config,
)