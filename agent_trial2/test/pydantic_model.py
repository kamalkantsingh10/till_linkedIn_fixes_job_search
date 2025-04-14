from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


model= OpenAIModel('gpt-4o-mini')


ollama_model = OpenAIModel(
    model_name='qwen2.5:latest', provider=OpenAIProvider(base_url='http://localhost:11434/v1')
)
agent =Agent(ollama_model)

print(agent.run_sync("who are you?"))