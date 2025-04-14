import typing

import fastapi
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from app.core.domain.storage.service.repositories import FileRetrievalError
from app.core.domain.storage.service.usecases import StorageUsecase

storage_router = fastapi.APIRouter(route_class=DishkaRoute)


@storage_router.post('/upload')
async def upload_file(
    usecase: FromDishka[StorageUsecase],
    file: fastapi.UploadFile,
) -> dict[typing.Literal['id'], str]:
    content = await file.read()
    identifier = await usecase.upload_file(content, content_type=file.content_type)

    return {'id': identifier}


@storage_router.get('/{identifier}')
async def download_file(
    usecase: FromDishka[StorageUsecase],
    identifier: typing.Annotated[str, fastapi.Path()],
) -> fastapi.responses.Response:
    try:
        content, mime = await usecase.download_file(identifier)

    except FileRetrievalError as error:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail='Couldnt retrieve file with given id.',
        ) from error

    return fastapi.responses.Response(
        content=content,
        status_code=fastapi.status.HTTP_200_OK,
        media_type=mime,
    )
