import json

import dishka

from app.core.domain.campaign.service.text_generators import TextGenerator
from app.core.infra.yandexgpt.interactors import (
    ResponseDecodingError,
    YandexGPTInteractor,
)


class YandexGPTTextGenerator(TextGenerator):
    def __init__(self, yandex_gpt_interactor: YandexGPTInteractor) -> None:
        self.interactor = yandex_gpt_interactor

    async def generate_text(self, text: str, prompt: str) -> str:
        result = await self.interactor.interact(prompt, text)

        try:
            generated_text = json.loads(result)['result']

        except json.JSONDecodeError as error:
            raise ResponseDecodingError from error

        return generated_text


generator_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
generator_provider.provide(YandexGPTTextGenerator, provides=TextGenerator)
