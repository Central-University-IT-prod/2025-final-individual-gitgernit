import dishka

from app.core.domain.campaign.service.moderators import Moderator


class MockModerator(Moderator):
    async def validate_text(self, _text: str, _prompt: str = '') -> bool:
        return True


moderator_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
moderator_provider.provide(MockModerator, provides=Moderator)
