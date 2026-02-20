from abc import ABC, abstractmethod
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from typing import Union, Any
from ..utils.logging import get_logger


class BaseAgent(ABC):
    def __init__(self, llm=None, name: str = "BaseAgent"):
        self._llm = llm
        self._name = name
        self._logger = get_logger(f"agents.{name}")

    @abstractmethod
    async def process(self, input_data: Union[list[BaseMessage], dict]) -> Union[list[BaseMessage], dict]:
        pass

    async def invoke(self, message: str, system_prompt: str | None = None):
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        result = await self.process(messages)
        return result[-1] if result else None

    def invoke_sync(self, messages: list[BaseMessage]):
        if not self._llm:
            raise NotImplementedError("LLM not available for sync invoke")
        return self._llm.invoke(messages)

    @property
    def name(self) -> str:
        return self._name

    def get_logger_prefix(self) -> str:
        return f"[{self._name}]"

    async def log(self, message: str, level: str = "info"):
        log_method = getattr(self._logger, level.lower(), self._logger.info)
        log_method(f"{self.get_logger_prefix()} {message}")

