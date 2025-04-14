import pytest

from app.core.infra.moderation.mock import MockModerator
from app.core.infra.text_generators.mock import MockTextGenerator


@pytest.fixture
def mock_text_generator() -> MockTextGenerator:
    return MockTextGenerator()


@pytest.fixture
def mock_moderator() -> MockModerator:
    return MockModerator()
