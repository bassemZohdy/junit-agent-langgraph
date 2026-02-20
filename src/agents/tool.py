from langchain_core.messages import BaseMessage, AIMessage
from .base import BaseAgent


class ToolAgent(BaseAgent):
    async def process(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        last_message = messages[-1]
        result = f"Tool processed: {last_message.content}"
        return [AIMessage(content=result)]
