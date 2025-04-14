import dataclasses

import aiogram
import aiogram.filters
import aiogram.fsm.state
import aiogram.types
import pydantic
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka.integrations.aiogram import FromDishka, inject

from app.core.domain.campaign.service.dto import CampaignDTO, Gender, TargetingDTO
from app.core.domain.campaign.service.usecases import CampaignUsecase
from app.core.infra.models.telegram_advertisers.interface import (
    TelegramAdvertisersRepository,
)

menu_router = aiogram.Router()


@menu_router.message(aiogram.filters.Command('menu'))
@inject
async def menu(
    message: aiogram.types.Message,
    state: FSMContext,
    repository: FromDishka[TelegramAdvertisersRepository],
    usecase: FromDishka[CampaignUsecase],
) -> None:
    advertiser_id = await repository.get_advertiser(str(message.from_user.id))
    campaigns = await usecase.get_advertiser_campaigns(advertiser_id)

    keyboard = InlineKeyboardBuilder()

    for campaign in campaigns:
        keyboard.button(
            text=campaign.ad_title,
            callback_data=f'campaign:{campaign.id}',
        )

    keyboard.button(
        text='Создать кампанию',
        callback_data='create_campaign',
    )

    keyboard.adjust(1)

    await message.answer('Ваши кампании:', reply_markup=keyboard.as_markup())


class CampaignCreationState(aiogram.fsm.state.StatesGroup):
    active = aiogram.fsm.state.State()


@dataclasses.dataclass
class Field:
    name: str
    text: str


questions = [
    Field(
        name='impressions_limit',
        text='Введите максимальное количество показов',
    ),
    Field(
        name='clicks_limit',
        text='Введите максимальное количество переходов',
    ),
    Field(
        name='cost_per_click',
        text='Введите стоимость за клик',
    ),
    Field(
        name='cost_per_impression',
        text='Введите стоимость за показ',
    ),
    Field(
        name='ad_title',
        text='Введите заголовок объявления',
    ),
    Field(
        name='ad_text',
        text='Введите текст объявления',
    ),
    Field(
        name='start_date',
        text='Введите дату начала кампании (число)',
    ),
    Field(
        name='end_date',
        text='Введите дату завершения кампании (число)',
    ),
    Field(
        name='gender',
        text='Выберите целевую аудиторию по полу (MALE / FEMALE / ALL) или -',
    ),
    Field(
        name='age_from',
        text='Введите минимальный возраст целевой аудитории или -',
    ),
    Field(
        name='age_to',
        text='Введите максимальный возраст целевой аудитории или -',
    ),
    Field(
        name='location',
        text='Введите местоположение целевой аудитории или -',
    ),
]


@menu_router.callback_query(aiogram.F.data == 'create_campaign')
async def start_campaign_creation(
    callback: aiogram.types.CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(CampaignCreationState.active)
    await state.update_data(step=0, answers={})

    question = questions[0]
    await callback.message.answer(
        'Пожалуйста, заполните следующие поля кампании. Валидация произойдет в конце.',
    )
    await callback.message.answer(question.text)
    await callback.answer()


@menu_router.message(aiogram.filters.StateFilter(CampaignCreationState.active))
@inject
async def process_campaign_answer(
    message: aiogram.types.Message,
    state: FSMContext,
    repository: FromDishka[TelegramAdvertisersRepository],
    usecase: FromDishka[CampaignUsecase],
) -> None:
    data = await state.get_data()
    step = data.get('step', 0)

    question = questions[step]
    data['answers'][question.name] = message.text if message.text != '-' else None

    step += 1
    if step < len(questions):
        data['step'] = step
        await state.update_data(data)
        new_question = questions[step]
        return await message.answer(new_question.text)

    await finalize_campaign(message, state, repository, usecase)
    return None


async def finalize_campaign(
    message: aiogram.types.Message,
    state: FSMContext,
    repository: TelegramAdvertisersRepository,
    usecase: CampaignUsecase,
) -> None:
    data = await state.get_data()
    answers = data['answers']

    advertiser_id = await repository.get_advertiser(str(message.from_user.id))
    if advertiser_id is None:
        await message.answer('Вы точно рекламодатель? Используйте /start')
        return

    try:
        targeting_dto = (
            TargetingDTO(
                gender=Gender(answers.get('gender')) if answers.get('gender') else None,
                age_from=int(answers.get('age_from'))
                if answers.get('age_from')
                else None,
                age_to=int(answers.get('age_to')) if answers.get('age_to') else None,
                location=answers.get('location') if answers.get('location') else None,
            )
            if any(
                answers.get(key) for key in ('gender', 'age_from', 'age_to', 'location')
            )
            else None
        )

        campaign_dto = CampaignDTO(
            advertiser_id=advertiser_id,
            impressions_limit=int(answers.get('impressions_limit'))
            if answers.get('impressions_limit')
            else None,
            clicks_limit=int(answers.get('clicks_limit'))
            if answers.get('clicks_limit')
            else None,
            cost_per_impression=float(answers.get('cost_per_impression'))
            if answers.get('cost_per_impression')
            else None,
            cost_per_click=float(answers.get('cost_per_click'))
            if answers.get('cost_per_click')
            else None,
            ad_title=answers['ad_title'],
            ad_text=answers['ad_text'],
            start_date=int(answers.get('start_date'))
            if answers.get('start_date')
            else None,
            end_date=int(answers.get('end_date')) if answers.get('end_date') else None,
            targeting=targeting_dto,
        )

    except (pydantic.ValidationError, ValueError, TypeError):
        await message.answer('Произошли ошибки валидации, перепроверьте поля :(')
        await state.clear()
        return

    dto = await usecase.create_campaign(campaign_dto)
    await message.answer(
        f'Вы успешно зарегистрировали кампанию "{dto.ad_title}". ID: {dto.id}',
    )
    await state.clear()
