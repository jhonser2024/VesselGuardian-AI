from autogen import AssistantAgent, UserProxyAgent
import gradio as gr


def run_assistant(message):
    config_list = [
    {
        "model": "llama2",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }
    ]

    assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})

    user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False})
    response = user_proxy.initiate_chat(assistant, message=message)

iface = gr.Interface(fn=run_assistant,inputs="text",outputs="text",title="Llama2")
iface.launch()