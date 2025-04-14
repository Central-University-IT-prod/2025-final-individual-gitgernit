import json

import dishka

from app.core.domain.campaign.service.moderators import Moderator
from app.core.infra.yandexgpt.interactors import (
    ResponseDecodingError,
    YandexGPTInteractor,
)

PROMPT = """
    Ты - модератор описаний рекламных кампаний. Тебе подается текст рекламной кампании.
    Инвалидируй только те тексты, которые содержат мат и ругательства
    (в прямой или очевидной, поверхностной завуалированной форме)
    Ты должен отвечать в формате JSON, твой ответ должен содержать два поля:
    {
        valid: {bool},
        detail: {str}
    }
    valid - валиден ли текст, detail - описание проблемы при valid = false.
    """


class YandexGPTModerator(Moderator):
    def __init__(self, yandex_gpt_interactor: YandexGPTInteractor) -> None:
        self.interactor = yandex_gpt_interactor

    async def validate_text(self, text: str, prompt: str = PROMPT) -> bool:
        result = await self.interactor.interact(prompt, text)

        try:
            verdict = json.loads(result)

        except json.JSONDecodeError as error:
            raise ResponseDecodingError from error

        valid, _detail = str(verdict['valid']).lower() == 'true', verdict['detail']

        return valid


moderator_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
moderator_provider.provide(YandexGPTModerator, provides=Moderator)
