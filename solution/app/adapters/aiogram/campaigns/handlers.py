import dataclasses
import uuid

import aiogram
import aiogram.filters.callback_data
import aiogram.fsm.state
import pydantic
from aiogram.fsm.context import FSMContext
from dishka.integrations.aiogram import FromDishka, inject

from app.core.domain.campaign.service.dto import CampaignDTO, Gender, TargetingDTO
from app.core.domain.campaign.service.usecases import (
    CampaignUsecase,
    InvalidCampaignError,
)
from app.core.domain.stats.service.usecases import StatsUsecase
from app.core.infra.models.telegram_advertisers.interface import (
    TelegramAdvertisersRepository,
)

campaigns_router = aiogram.Router()


class CampaignCallback(aiogram.filters.callback_data.CallbackData, prefix='campaign'):
    campaign_id: str


class DeleteCampaignCallback(aiogram.filters.callback_data.CallbackData, prefix='dc'):
    campaign_id: str


class PutCampaignCallback(aiogram.filters.callback_data.CallbackData, prefix='pc'):
    campaign_id: str


@campaigns_router.callback_query(CampaignCallback.filter())
@inject
async def show_campaign(
    query: aiogram.types.CallbackQuery,
    repository: FromDishka[TelegramAdvertisersRepository],
    campaign_usecase: FromDishka[CampaignUsecase],
    stats_usecase: FromDishka[StatsUsecase],
) -> None:
    data = CampaignCallback.unpack(query.data)

    await repository.get_advertiser(str(query.from_user.id))
    campaign_id = uuid.UUID(data.campaign_id)

    campaign = await campaign_usecase.get_campaign(campaign_id)
    stats = await stats_usecase.get_total_campaign_stats(campaign.id)

    stats_message = (
        f'Показы: {stats.impressions_count}\n'
        f'Потрачено на показы: {stats.spent_impressions}\n'
        f'Клики: {stats.clicks_count}\n'
        f'Потрачено на клики: {stats.spent_clicks}\n'
        f'Конверсия: {stats.conversion}%\n'
        f'Общие затраты: {stats.spent_total}'
    )

    keyboard = aiogram.types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                aiogram.types.InlineKeyboardButton(
                    text='Удалить кампанию',
                    callback_data=f'dc:{campaign.id}',
                ),
                aiogram.types.InlineKeyboardButton(
                    text='Изменить кампанию',
                    callback_data=f'pc:{campaign.id}',
                ),
            ],
        ],
    )

    await query.message.delete()
    await query.message.answer(
        f'{campaign.ad_title}\n{campaign.ad_text}\n\n{stats_message}',
        reply_markup=keyboard,
    )
    await query.answer()


@campaigns_router.callback_query(DeleteCampaignCallback.filter())
@inject
async def delete_campaign(
    query: aiogram.types.CallbackQuery,
    repository: FromDishka[TelegramAdvertisersRepository],
    campaign_usecase: FromDishka[CampaignUsecase],
) -> None:
    data = DeleteCampaignCallback.unpack(query.data)

    advertiser_id = await repository.get_advertiser(str(query.from_user.id))
    campaign_id = uuid.UUID(data.campaign_id)

    await campaign_usecase.delete_campaign(campaign_id, advertiser_id)

    await query.answer('Кампания успешно удалена!')
    await query.message.delete()


class CampaignPutState(aiogram.fsm.state.StatesGroup):
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


@campaigns_router.callback_query(PutCampaignCallback.filter())
async def start_campaign_put(
    callback: aiogram.types.CallbackQuery,
    state: FSMContext,
) -> None:
    data = PutCampaignCallback.unpack(callback.data)

    await state.set_state(CampaignPutState.active)
    await state.update_data(step=0, answers={}, campaign_id=data.campaign_id)

    question = questions[0]
    await callback.message.answer(
        'Пожалуйста, заполните следующие поля кампании. Валидация произойдет в конце.',
    )
    await callback.message.answer(question.text)
    await callback.answer()


@campaigns_router.message(aiogram.filters.StateFilter(CampaignPutState.active))
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
        await message.answer(new_question.text)
        return

    await finalize_campaign(message, state, repository, usecase)
    return


async def finalize_campaign(
    message: aiogram.types.Message,
    state: FSMContext,
    repository: TelegramAdvertisersRepository,
    usecase: CampaignUsecase,
) -> None:
    data = await state.get_data()
    answers = data['answers']
    campaign_id = uuid.UUID(data['campaign_id'])

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
        dto = await usecase.patch_campaign(campaign_id, campaign_dto)

    except (InvalidCampaignError, pydantic.ValidationError, ValueError, TypeError):
        await message.answer('Произошли ошибки валидации, перепроверьте поля :(')
        await state.clear()
        return

    await message.answer(f'Вы успешно изменили кампанию "{dto.ad_title}". ID: {dto.id}')
    await state.clear()
