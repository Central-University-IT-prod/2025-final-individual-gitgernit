import pathlib

import pytest

from app.core.infra.storage.filesystem.repository import FilesystemStorageRepository


@pytest.fixture
def filesystem_storage_repository(
    tmp_path: pathlib.Path,
) -> FilesystemStorageRepository:
    return FilesystemStorageRepository(base_path=str(tmp_path.resolve()))
