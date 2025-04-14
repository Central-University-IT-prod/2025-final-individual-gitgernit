import mimetypes
import uuid

import aioboto3
import botocore.errorfactory
import dishka

from app.core.domain.storage.service.repositories import (
    FileRetrievalError,
    StorageRepository,
)


class S3StorageRepository(StorageRepository):
    def __init__(
        self,
        access_key_id: str,
        access_key: str,
        bucket: str,
    ) -> None:
        self.endpoint = 'https://storage.yandexcloud.net'
        self.access_key_id = access_key_id
        self.access_key = access_key
        self.bucket = bucket

    async def upload_file(
        self,
        content: bytes,
        content_type: str = 'application/octet-stream',
    ) -> str:
        session = aioboto3.Session()
        key = str(uuid.uuid4())

        async with session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.access_key,
        ) as s3:
            await s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content,
                ContentType=content_type,
            )

        return key

    async def download_file(self, file_id: str) -> tuple[bytes, str]:
        session = aioboto3.Session()

        async with session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.access_key,
        ) as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket, Key=file_id)
                content = await response['Body'].read()
                content_type = response.get('ContentType', 'application/octet-stream')

            except botocore.errorfactory.ClientError as error:
                raise FileRetrievalError from error

            return content, content_type


def get_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


class StorageProvider(dishka.Provider):
    scope = dishka.Scope.REQUEST

    def __init__(
        self,
        access_key_id: str,
        access_key: str,
        bucket: str,
    ) -> None:
        super().__init__()
        self.access_key_id = access_key_id
        self.access_key = access_key
        self.bucket = bucket

    @dishka.provide(provides=StorageRepository)
    async def get_storage(self) -> S3StorageRepository:
        return S3StorageRepository(
            self.access_key_id,
            self.access_key,
            self.bucket,
        )
