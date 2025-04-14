import dataclasses
import typing
import uuid

import aiogram
import aiogram.filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, SceneRegistry, on
from dishka.integrations.aiogram import FromDishka, inject

from app.core.domain.advertiser.service.dto import AdvertiserDTO
from app.core.domain.advertiser.service.usecases import AdvertiserUsecase
from app.core.infra.models.telegram_advertisers.interface import (
    TelegramAdvertisersRepository,
)

if typing.TYPE_CHECKING:
    import dishka

main_router = aiogram.Router()
registry = SceneRegistry(main_router)


@main_router.message.outer_middleware
async def registration_middleware(
    handler: typing.Callable[
        [aiogram.types.Message, dict[str, typing.Any]],
        typing.Awaitable[typing.Any],
    ],
    event: aiogram.types.Message,
    data: dict[str, typing.Any],
) -> typing.Any:
    state: FSMContext = data['state']

    if await state.get_state() is not None or event.text == '/start':
        return await handler(event, data)

    container: dishka.AsyncContainer = data['dishka_container']
    repository = await container.get(TelegramAdvertisersRepository)

    advertiser = await repository.get_advertiser(str(event.from_user.id))

    if advertiser is None:
        await event.answer('Используйте /start для регистрации.')
        return None

    return await handler(event, data)


@dataclasses.dataclass
class Field:
    name: str
    text: str


questions = [
    Field(
        name='name',
        text='Введите имя рекламодателя',
    ),
]


class RegistrationScene(Scene, state='registration'):
    @on.message.enter()
    @inject
    async def on_enter(
        self,
        message: aiogram.types.Message,
        state: FSMContext,
        repository: FromDishka[TelegramAdvertisersRepository],
    ) -> None:
        if (
            await repository.get_advertiser(telegram_id=str(message.from_user.id))
            is not None
        ):
            await self.wizard.exit(success=False)
            await message.answer(
                'Вы уже зарегистрированы. Используйте /menu для получения меню команд.',
            )
            return

        data = await state.get_data()
        data['step'] = 0
        data['answers'] = {}
        await state.set_data(data)

        question = questions[data['step']]

        await message.answer(
            'Добро пожаловать в ad-dicted! '
            'Пожалуйста, зарегистрируйтесь как рекламодатель:',
        )
        await message.answer(question.text)

    @on.message(aiogram.F.text)
    async def on_answer(
        self,
        message: aiogram.types.Message,
        state: FSMContext,
    ) -> None:
        data = await state.get_data()
        step = data['step']

        question = questions[step]

        data['answers'][question.name] = message.text
        data[step] = step + 1 if step + 1 < len(questions) else None
        await state.set_data(data)

        if data[step] is not None:
            new_question = questions[data[step]]
            await message.answer(new_question.text)
            return

        await self.wizard.exit(success=True)
        return

    @on.message.exit()
    @inject
    async def on_exit(
        self,
        message: aiogram.types.Message,
        state: FSMContext,
        repository: FromDishka[TelegramAdvertisersRepository],
        usecase: FromDishka[AdvertiserUsecase],
        *,
        success: bool = False,
    ) -> None:
        if not success:
            return

        data = await state.get_data()
        answers = data['answers']

        dto = AdvertiserDTO(
            id=uuid.uuid4(),
            name=answers['name'],
        )
        dto = await usecase.create_advertiser(dto)

        await repository.create_user(
            telegram_id=str(message.from_user.id),
            advertiser_id=dto.id,
        )

        await message.answer(
            f'Вы успешно зарегистрировали рекламодателя "{dto.name}". ID: {dto.id}',
        )


main_router.message.register(
    RegistrationScene.as_handler(),
    aiogram.filters.Command('start'),
)
registry.add(RegistrationScene)
