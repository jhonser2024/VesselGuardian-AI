import gradio as gr
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from autogen import ConversableAgent


Operator = Literal["+", "-", "*", "/"]

def calculator(a: int, b: int, operator: Annotated[Operator, "operator"]) -> int:
    print("Intentando tales de milato...")

    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return int(a / b)
    else:
        raise ValueError("Invalid operator")
    
def run_assistant(message):
    config_list = [
    {
        "model": "llama2",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }
    ]

    assistant = ConversableAgent(
        name="Assistant",
        system_message="You are a helpful AI assistant. "
        "You can help with simple calculations. "
        "Return 'TERMINATE' when the task is done.",
        llm_config={"config_list": config_list},
    )

    # The user proxy agent is used for interacting with the assistant agent
    # and executes tool calls.
    user_proxy = ConversableAgent(
        name="User",
        llm_config=False,
        is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
        human_input_mode="NEVER",
    )

    # Register the tool signature with the assistant agent.
    assistant.register_for_llm(name="calculator", description="A simple calculator")(calculator)

    # Register the tool function with the user proxy agent.
    user_proxy.register_for_execution(name="calculator")(calculator)


    chat_result = user_proxy.initiate_chat(assistant, message=message)

    return chat_result

iface = gr.Interface(fn=run_assistant,inputs="text",outputs="text",title="Llama2")
iface.launch()