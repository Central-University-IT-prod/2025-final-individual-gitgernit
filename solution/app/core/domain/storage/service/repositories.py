import abc


class FileRetrievalError(Exception):
    def __init__(self) -> None:
        super().__init__('Couldnt retrieve file.')


class StorageRepository(abc.ABC):
    @abc.abstractmethod
    async def upload_file(
        self,
        content: bytes,
        content_type: str = 'application/octet-stream',
    ) -> str:
        pass

    @abc.abstractmethod
    async def download_file(self, file_id: str) -> tuple[bytes, str]:
        pass
