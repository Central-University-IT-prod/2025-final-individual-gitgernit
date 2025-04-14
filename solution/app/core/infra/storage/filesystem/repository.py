import pathlib
import uuid

import aiofiles
import dishka

from app.core.infra.storage.s3.repository import StorageRepository


class FilesystemStorageRepository(StorageRepository):
    def __init__(self, base_path: str) -> None:
        self.base_path = pathlib.Path(base_path)

        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        content: bytes,
        _content_type: str = 'application/octet-stream',
    ) -> str:
        file_id = str(uuid.uuid4())
        file_path = self.base_path / file_id

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        return file_id

    async def download_file(self, file_id: str) -> tuple[bytes, str]:
        file_path = self.base_path / file_id

        if not file_path.exists():
            msg = f'File with ID {file_id} not found.'
            raise FileNotFoundError(msg)

        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()

        return content, 'application/octet-stream'


class StorageProvider(dishka.Provider):
    scope = dishka.Scope.REQUEST

    def __init__(
        self,
        base_path: str,
    ) -> None:
        super().__init__()
        self.base_path = base_path

    @dishka.provide(provides=StorageRepository)
    async def get_storage(self) -> FilesystemStorageRepository:
        return FilesystemStorageRepository(self.base_path)
