import abc


class TextGenerator(abc.ABC):
    @abc.abstractmethod
    async def generate_text(self, text: str, prompt: str) -> str:
        pass
