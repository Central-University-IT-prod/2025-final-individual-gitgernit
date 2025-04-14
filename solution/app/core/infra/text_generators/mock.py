import dishka

from app.core.domain.campaign.service.text_generators import TextGenerator


class MockTextGenerator(TextGenerator):
    async def generate_text(self, _text: str, _prompt: str) -> str:
        return 'арсений пархунов'


generator_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
generator_provider.provide(MockTextGenerator, provides=TextGenerator)
