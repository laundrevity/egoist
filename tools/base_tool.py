from abc import ABC, abstractmethod
from pydantic import BaseModel


class BaseTool(ABC):
    input_model = BaseModel
    description = ""

    def __init__(self, toolkit):
        self.toolkit = toolkit

    @abstractmethod
    async def execute(self, args: BaseModel) -> str:
        ...
