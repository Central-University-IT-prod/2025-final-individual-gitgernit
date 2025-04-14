import abc


class Moderator(abc.ABC):
    @abc.abstractmethod
    async def validate_text(self, text: str) -> bool:
        pass
