from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .schrema import Items  
from aiogram.types import InputMediaPhoto
from config import redis_db
import uuid
import json

item_router = Router()

MODERATOR_CHAT_ID = -1002458571043  

class ProductForm(StatesGroup):
    is_anonymous = State()
    contact = State()
    name = State()
    description = State()
    photos = State()
    price = State()
    confirm = State()

class EditForm(StatesGroup):
    name = State()
    description = State()
    photos = State()
    price = State()

def get_anonymity_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="anonymity_yes"),
         InlineKeyboardButton(text="Нет", callback_data="anonymity_no")],
        [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
    ])

def get_review_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправить", callback_data="send_product"),
         InlineKeyboardButton(text="Редактировать", callback_data="edit_product")]
    ])
def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
    ])
def get_photo_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="cancel")],
        [InlineKeyboardButton(text="Завершить загрузку", callback_data="finish_upload")]
    ])

@item_router.message(Command("post_product"))
async def post_product(message: types.Message, state: FSMContext):
    await message.answer("Вы хотите разместить товар анонимно?", reply_markup=get_anonymity_keyboard())
    await state.set_state(ProductForm.is_anonymous)

@item_router.callback_query(lambda c: c.data in ["anonymity_yes", "anonymity_no"])
async def handle_anonymity(callback_query: types.CallbackQuery, state: FSMContext):
    is_anon = callback_query.data == "anonymity_yes"
    await state.update_data(is_anonymous=is_anon)

    if is_anon:
        await callback_query.message.edit_text(
            "Напишите название товара.",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(ProductForm.name)
    else:
        await callback_query.message.edit_text(
            "Пришлите контакт для связи.",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(ProductForm.contact)


@item_router.callback_query(lambda c: c.data == "cancel")
async def handle_cancel(callback_query: types.CallbackQuery, state: FSMContext):
 
    current_state = await state.get_state()

    if current_state in [ProductForm.name.state, ProductForm.description.state, ProductForm.photos.state, ProductForm.price.state,
                         EditForm.name.state, EditForm.description.state, EditForm.photos.state, EditForm.price.state]:

        await callback_query.message.edit_text(
            "Цена сохранена. Вы хотите отправить объявление или внести изменения?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Отправить", callback_data="send_product")],
                [InlineKeyboardButton(text="Редактировать", callback_data="edit_product")],
                [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
            ])
        )
    else:

        await state.clear()
        await callback_query.message.edit_text("Процесс размещения товара был отменён.")

@item_router.message(ProductForm.contact)
async def handle_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await message.answer(
        "Напишите название товара.",
        reply_markup=get_cancel_keyboard() 
    )
    await state.set_state(ProductForm.name)

@item_router.message(ProductForm.name)
async def handle_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Напишите описание товара.",
        reply_markup=get_cancel_keyboard() 
    )
    await state.set_state(ProductForm.description)


@item_router.message(ProductForm.description)
async def handle_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "Прикрепите фотографии товара.",
        reply_markup=get_cancel_keyboard() 
    )
    await state.set_state(ProductForm.photos)

@item_router.message(ProductForm.photos, F.photo)
async def handle_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(
        "Фото добавлено. Прикрепите ещё или завершите.",
        reply_markup=get_photo_keyboard() 
    )

@item_router.callback_query(lambda c: c.data == "finish_upload")
async def handle_finish_upload(callback_query: types.CallbackQuery, state: FSMContext):

    await callback_query.message.edit_text("Введите цену товара.", reply_markup=get_cancel_keyboard())
    await state.set_state(ProductForm.price)

@item_router.message(ProductForm.price)
async def handle_price(message: types.Message, state: FSMContext):

    await state.update_data(price=message.text)
    
    await message.answer(
        "Цена сохранена. Вы хотите отправить объявление или внести изменения?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить", callback_data="send_product")],
            [InlineKeyboardButton(text="Редактировать", callback_data="edit_product")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")] 
        ])
    )

@item_router.callback_query(lambda c: c.data == "edit_product")
async def edit_product(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "Какую часть объявления вы хотите изменить?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Название", callback_data="edit_name")],
            [InlineKeyboardButton(text="Описание", callback_data="edit_description")],
            [InlineKeyboardButton(text="Фотографии", callback_data="edit_photos")],
            [InlineKeyboardButton(text="Цена", callback_data="edit_price")],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ])
    )

@item_router.callback_query(lambda c: c.data == "edit_name")
async def start_edit_name(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите новое название товара:", reply_markup=get_cancel_keyboard())
    await state.set_state(EditForm.name)


@item_router.callback_query(lambda c: c.data == "edit_description")
async def start_edit_description(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите новое описание товара:", reply_markup=get_cancel_keyboard())
    await state.set_state(EditForm.description)


@item_router.callback_query(lambda c: c.data == "edit_photos")
async def start_edit_photos(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if photos:
        for idx, photo_id in enumerate(photos):
            delete_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Удалить фото", callback_data=f"delete_photo_{idx}")]
            ])
            await callback_query.message.answer_photo(photo=photo_id, caption=f"Фото {idx+1}", reply_markup=delete_markup)
    else:
        await callback_query.message.answer("У вас нет загруженных фотографий.")

    await callback_query.message.answer(
        "Прикрепите новые фотографии товара или нажмите Завершить редактирование'.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Завершить редактирование", callback_data="finish_photo_edit")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
        ])
    )
    await state.set_state(EditForm.photos)

@item_router.callback_query(lambda c: c.data.startswith("delete_photo_"))
async def delete_photo(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    idx = int(callback_query.data.split("_")[-1])
    if 0 <= idx < len(photos):
        deleted_photo_id = photos.pop(idx)
        await state.update_data(photos=photos)
        await callback_query.answer("Фото удалено.")
        await callback_query.message.delete()
    else:
        await callback_query.answer("Не удалось удалить фото.")
@item_router.callback_query(lambda c: c.data == "finish_photo_edit")
async def finish_photo_edit(callback_query: types.CallbackQuery, state: FSMContext):

    await callback_query.message.answer(
        "Фотографии обновлены. Вы хотите отправить объявление или внести изменения?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить", callback_data="send_product")],
            [InlineKeyboardButton(text="Редактировать", callback_data="edit_product")]
        ])
    )
    await state.set_state(ProductForm.confirm)

@item_router.callback_query(lambda c: c.data == "edit_price")
async def start_edit_price(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите новую цену товара:", reply_markup=get_cancel_keyboard())
    await state.set_state(EditForm.price)



@item_router.message(EditForm.name)
async def handle_edit_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(
        "Название обновлено. Вы хотите отправить объявление или внести изменения?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить", callback_data="send_product")],
            [InlineKeyboardButton(text="Редактировать", callback_data="edit_product")]
        ])
    )


@item_router.message(EditForm.description)
async def handle_edit_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)

    await message.answer(
        "Описание обновлено. Вы хотите отправить объявление или внести изменения?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить", callback_data="send_product")],
            [InlineKeyboardButton(text="Редактировать", callback_data="edit_product")]
        ])
    )

@item_router.message(EditForm.photos, F.photo)
async def handle_edit_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    await message.answer(
        "Фотографии обновлены. Вы хотите отправить объявление или внести изменения?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить", callback_data="send_product")],
            [InlineKeyboardButton(text="Редактировать", callback_data="edit_product")]
        ])
    )


@item_router.message(EditForm.price)
async def handle_edit_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)

    await message.answer(
        "Цена обновлена. Вы хотите отправить объявление или внести изменения?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить", callback_data="send_product")],
            [InlineKeyboardButton(text="Редактировать", callback_data="edit_product")]
        ])
    )

@item_router.callback_query(lambda c: c.data == "send_product")
async def send_product(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    is_anonymous = data.get("is_anonymous", False)
    contact = "Анонимно" if is_anonymous else data.get("contact")

    item_id = str(uuid.uuid4())

    item = Items(
        id=item_id,
        category_id="default_category", 
        title=data["name"],
        description=data["description"],
        condition="new", 
        address=contact,
        cost=data["price"],
        status="pending",
        seller_id=str(callback_query.from_user.id),
    )

    redis_db.set(item_id, json.dumps(item.__dict__))    
    photos = data.get("photos", [])
    if photos:
        media = [InputMediaPhoto(media=photos[0], caption=str(item), parse_mode="HTML")]
        for photo in photos[1:]:
            media.append(InputMediaPhoto(media=photo))
        await callback_query.bot.send_media_group(chat_id=MODERATOR_CHAT_ID, media=media)
    else:
        await callback_query.bot.send_message(
            chat_id=MODERATOR_CHAT_ID, 
            text=str(item), 
            parse_mode="HTML"
        )

    try:
        await callback_query.message.delete()
    except Exception as e:
        pass

    await callback_query.message.answer("Ваше объявление отправлено на модерацию.")
    await state.clear()

