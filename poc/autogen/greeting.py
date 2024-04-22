import autogen
from typing import Literal
from typing_extensions import Annotated

local_llm_config={
    "config_list": [
        {
            "model": "NotRequired", # Loaded with LiteLLM command
            "api_key": "NotRequired", # Not needed
            "base_url": "http://0.0.0.0:4000"  # Your LiteLLM URL
        }
    ],
    "cache_seed": None # Turns off caching, useful for testing different models
}

# Create the agent and include examples of the function calling JSON in the prompt
# to help guide the model
agent = autogen.AssistantAgent(
    name="Agente saludador",
    system_message="Para las tareas de codificación, utiliza solo las funciones que te hayan sido proporcionadas. Responde TERMINATE cuando la tarea esté completada.",
    llm_config=local_llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
)


# Define our function that we expect to call
def greeting(mensaje: str ) -> str:
    return f"Me has saludado con este mensaje {mensaje}"

# Register the function with the agent
@user_proxy.register_for_execution()
@agent.register_for_llm(description="Usa esta herramienta cuando necesites saludar.")
def greeting_calculator(
    name: Annotated[str, "Mensaje "]
) -> str:
    result =  greeting(name)
    return result

# start the conversation
res = user_proxy.initiate_chat(
    agent,
    message="Hola te mando este saludo, 'Buenos dias camarada cvb'",
    summary_method="reflection_with_llm",
)

print("Ajam ya yo ya y tales",res)