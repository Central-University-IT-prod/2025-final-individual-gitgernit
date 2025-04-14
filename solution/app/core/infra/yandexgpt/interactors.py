import json

import aiohttp
import dishka

YANDEX_GPT_COMPLETION_URL = (
    'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
)


class ResponseDecodingError(Exception):
    def __init__(self) -> None:
        super().__init__('Couldnt decode Yandex GPT request.')


class UnavailableError(Exception):
    def __init__(self) -> None:
        super().__init__('Couldnt retrieve answer from Yandex GPT.')


class YandexGPTInteractor:
    def __init__(
        self,
        catalog_identifier: str,
        api_key: str,
    ) -> None:
        self._catalog_identifier = catalog_identifier
        self._api_key = api_key

    async def interact(self, prompt: str, text: str) -> str:
        prompt_payload = {
            'modelUri': f'gpt://{self._catalog_identifier}/yandexgpt-lite',
            'completionOptions': {
                'stream': False,
                'temperature': 0,
                'maxTokens': 150,
            },
            'messages': [
                {'role': 'system', 'text': prompt},
                {'role': 'user', 'text': text},
            ],
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {self._api_key}',
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    YANDEX_GPT_COMPLETION_URL,
                    headers=headers,
                    json=prompt_payload,
                    timeout=10,
                ) as response:
                    result = await response.json()

                    return result['result']['alternatives'][0]['message']['text'].strip(
                        '`',
                    )

            except (json.JSONDecodeError, KeyError) as error:
                raise ResponseDecodingError from error

            except TimeoutError as error:
                raise UnavailableError from error


class InteractorProvider(dishka.Provider):
    scope = dishka.Scope.REQUEST

    def __init__(self, catalog_identifier: str, api_key: str) -> None:
        super().__init__()

        self.catalog_identifier = catalog_identifier
        self.api_key = api_key

    @dishka.provide
    async def get_interactor(self) -> YandexGPTInteractor:
        return YandexGPTInteractor(self.catalog_identifier, self.api_key)
