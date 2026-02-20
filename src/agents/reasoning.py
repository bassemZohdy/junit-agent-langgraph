from langchain_core.messages import BaseMessage
from .base import BaseAgent


class ReasoningAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="ReasoningAgent")

    async def process(self, input_data: list[BaseMessage]) -> list[BaseMessage]:
        if not self._llm:
            raise RuntimeError("LLM not configured")
        response = await self._llm.ainvoke(input_data)
        return [response]
