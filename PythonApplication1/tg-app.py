# WARNING: ts file is vibecoded all questions related to gpt-4.1 xD
import os
import dotenv
import logging as log
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from charCreate import CharCreate
from r34nfag import Rule34NewForAnimeGooners

dotenv.load_dotenv()
log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise Exception('TELEGRAM_BOT_TOKEN is missing in .env!')
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

char_creator = CharCreate()
rule34 = Rule34NewForAnimeGooners()

func_steps = [
    ("who", char_creator.choose_who),
    ("body_type", char_creator.choose_body_type),
    ("hair_style", char_creator.choose_hair_style),
    ("hair_color", char_creator.choose_hair_color),
    ("eyes", char_creator.choose_eyes),
    ("clothes", char_creator.choose_clothes),
    ("pose_action", char_creator.choose_pose_action),
    ("setting", char_creator.choose_setting),
    ("mood", char_creator.choose_mood),
    ("personality", char_creator.choose_personality),
    ("accessories_props", char_creator.choose_accessories_props),
    ("genre_theme", char_creator.choose_genre_theme),
    ("time_weather", char_creator.choose_time_weather),
    ("girls", char_creator.choose_girls),
    ("boys", char_creator.choose_boys)
]

class CharFSM(StatesGroup):
    step = State()
    result = State()

def build_step_keyboard(group, idx, tags, idx_selected=None, is_last=False):
    max_btns = 4
    kb = []
    for i, tag in enumerate(tags):
        selected = idx_selected and i in idx_selected
        btn_text = f"✅ {tag}" if selected else tag
        kb.append(InlineKeyboardButton(text=btn_text, callback_data=f"pick_{idx}_{i}"))
    arranged = [kb[j:j+max_btns] for j in range(0, len(kb), max_btns)]
    nav = []
    if idx > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{idx}"))
    nav.append(InlineKeyboardButton(text="✅ Готово", callback_data=f"commit_{idx}"))
    nav.append(InlineKeyboardButton(text="⏭️ Пропустить", callback_data=f"skip_{idx}"))
    nav.append(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    arranged.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=arranged)

@dp.callback_query(F.data.startswith("commit_"))
async def commit_handler(call: CallbackQuery, state: FSMContext):
    parts = call.data.split('_')
    if len(parts) != 2: await call.answer("Ошибка данных кнопки."); return
    idx = int(parts[1])
    await state.update_data(step_index=idx+1)
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)

async def send_step(message_obj, state: FSMContext, preview=False):
    data = await state.get_data()
    idx = data.get('step_index', 0)
    answers = data.get("answers", {})
    prev_char = ""
    try:
        char_creator.char = ""
        for i in range(idx):
            group, func = func_steps[i]
            answer = answers.get(group)
            if answer is not None:
                # если список — проходи по элементам (мультивыбор)
                if isinstance(answer, list):
                    for a in answer:
                        func(a)
                else:
                    func(answer)
        prev_char = char_creator.get_character()
    except Exception as e:
        prev_char = f"[ошибка превью: {e}]"

    if preview and prev_char:
        try:
            await message_obj.answer(
                f"📝 <b>Текущий персонаж:</b>\n<code>{prev_char or '—'}</code>", parse_mode="HTML"
            )
        except Exception:
            pass

    if idx >= len(func_steps):
        char_creator.char = ""
        for i, (group, func) in enumerate(func_steps):
            ans = answers.get(group)
            if ans is not None:
                if isinstance(ans, list):
                    for a in ans:
                        func(a)
                else:
                    func(ans)
        desc = char_creator.get_character()
        if not desc.strip():
            await message_obj.answer("Некорректный персонаж, прерываю 😭")
            await state.clear()
            return

        # --- Rule34 GENERATION ---
        await message_obj.answer(
            f"<b>Готово!</b> Ваш персонаж:\n<code>{desc}</code>\n\nДелаю запрос...", parse_mode="HTML"
        )
        posts = []
        for page in range(1, 6):   # 1..5 -> pid=0..4
            chunk = rule34.make_rule34_request(desc, pid=page-1, limit=10)
            if not isinstance(chunk, list) or not chunk:
                break
            posts.extend(chunk)
            if len(posts) >= 50:
                break
        posts = posts[:50]
        await state.set_state(CharFSM.result)
        await state.update_data(result_posts=posts, result_desc=desc, result_idx=0)
        await show_result(message_obj, state)
        return

    group, _ = func_steps[idx]
    try:
        all_tags = char_creator.get_tags()
        tags = all_tags[group]
    except Exception as e:
        await message_obj.answer(f"Ошибка загрузки вариантов для {group}: {e}")
        await state.clear()
        return

    idx_selected = answers.get(group, [])
    if idx_selected is None:
        idx_selected = []
    # показывать шаг + название группы
    text = f"Шаг <b>{idx+1}/{len(func_steps)}</b>\nВыберите <b>{group.replace('_', ' ').capitalize()}</b>:"

    # если что-то выбрано — красиво покажем
    if idx_selected:
        sel_txt = ", ".join(tags[i] for i in idx_selected if 0 <= i < len(tags))
        text += f"\n\n<b>Твои теги:</b>\n<code>{sel_txt or '—'}</code>"

    kb = build_step_keyboard(group, idx, tags, idx_selected=idx_selected)
    await message_obj.answer(text, parse_mode="HTML", reply_markup=kb)

async def show_result(message_or_call, state: FSMContext, edit=False):
    data = await state.get_data()
    resp = data.get('result_posts', [])
    desc = data.get('result_desc', "")
    idx = data.get('result_idx', 0)
    total = len(resp)
    if not resp:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✏ Изменить запрос", callback_data="result_edit")]
            ]
        )
        await send_result_message(message_or_call, "😢 <b>Ничего не найдено!</b>\nПопробуйте изменить запрос.", kb, edit)
        return
    post = resp[idx]
    img_url = post.get("file_url") or post.get("sample_url")
    nav = []
    if idx > 0:
        nav.append(InlineKeyboardButton(text='⬅️ Назад', callback_data='result_prev'))
    if idx < total - 1:
        nav.append(InlineKeyboardButton(text='⏭️ Далее', callback_data='result_next'))
    nav.append(InlineKeyboardButton(text="✏ Изменить запрос", callback_data="result_edit"))
    kb = InlineKeyboardMarkup(inline_keyboard=[nav])
    caption = f"<b>Результат {idx + 1} из {total}</b>\n<code>{desc}</code>"
    await send_result_message(message_or_call, caption, kb, edit, img_url)

async def send_result_message(message_or_call, caption, kb, edit, img_url=None):
    msg = message_or_call.message if isinstance(message_or_call, types.CallbackQuery) else message_or_call
    if edit and img_url:
        try:
            await msg.edit_media(
                types.InputMediaPhoto(media=img_url, caption=caption, parse_mode="HTML"),
                reply_markup=kb
            )
        except Exception:
            await msg.edit_caption(caption=caption, parse_mode="HTML", reply_markup=kb)
    elif edit:
        await msg.edit_caption(caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        if img_url:
            await msg.answer_photo(img_url, caption=caption, parse_mode="HTML", reply_markup=kb)
        else:
            await msg.answer(caption, parse_mode="HTML", reply_markup=kb)

# --- STEP NAVIGATION ---
@dp.callback_query(F.data.startswith("pick_"))
async def pick_handler(call: CallbackQuery, state: FSMContext):
    parts = call.data.split('_')
    if len(parts) != 3: await call.answer("Ошибка данных кнопки."); return
    idx = int(parts[1])
    val = int(parts[2])
    data = await state.get_data()
    answers = data.get("answers", {})
    group, _= func_steps[idx]
    selected = answers.get(group, [])
    if selected is None: selected = []
    if val in selected:
        selected.remove(val)
    else:
        selected.append(val)
    answers[group] = selected
    await state.update_data(step_index=idx, answers=answers)
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)


@dp.callback_query(F.data.startswith("skip_"))
async def skip_handler(call: CallbackQuery, state: FSMContext):
    parts = call.data.split('_')
    if len(parts) != 2: return await call.answer("Ошибка данных кнопки.")
    idx = int(parts[1])
    data = await state.get_data()
    answers = data.get("answers", {})
    group, _ = func_steps[idx]
    answers[group] = None
    await state.update_data(step_index=idx + 1, answers=answers)
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)

@dp.callback_query(F.data.startswith("prev_"))
async def prev_handler(call: CallbackQuery, state: FSMContext):
    parts = call.data.split('_')
    if len(parts) != 2: return await call.answer("Ошибка данных кнопки.")
    idx = int(parts[1])
    if idx == 0:
        await call.answer("Это первый шаг!")
        return
    data = await state.get_data()
    answers = data.get("answers", {})
    await state.update_data(step_index=idx - 1, answers=answers)
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)

@dp.callback_query(F.data == "cancel")
async def cancel_cb_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try: await call.message.delete()
    except Exception: pass
    await call.message.answer("Создание персонажа отменено. жми /start, если хочешь снова попробовать! 🥶")

# --- RESULT NAVIGATION ---
@dp.callback_query(F.data.in_({"result_next", "result_prev"}))
async def cb_result_nav(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    idx = data.get("result_idx", 0)
    total = len(data.get('result_posts', []))
    if call.data == "result_next":
        if idx >= total - 1:
            await call.answer("Это последний результат!")
        else:
            await state.update_data(result_idx=idx + 1)
            await call.answer()
            await show_result(call, state, edit=True)
    else:
        if idx <= 0:
            await call.answer("Это первый результат!")
        else:
            await state.update_data(result_idx=idx - 1)
            await call.answer()
            await show_result(call, state, edit=True)

@dp.callback_query(F.data == "result_edit")
async def cb_result_edit(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    answers = data.get("answers", {})
    await state.set_state(CharFSM.step)
    await state.update_data(
        step_index=len(func_steps)-1,
        answers=answers
    )
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)

# --- СТАРТ ---
@dp.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(CharFSM.step)
    await state.update_data(step_index=0, answers={})
    await send_step(message, state, preview=True)

@dp.message(Command('reset'))
async def cmd_reset(message: types.Message, state: FSMContext):
    await state.clear()
    await cmd_start(message, state)

@dp.message(Command('cancel'))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Создание персонажа отменено. Жми /start если захочешь снова!")

@dp.message(Command('preview'))
async def cmd_preview(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get("answers", {})
    char_creator.char = ""
    for i, (group, func) in enumerate(func_steps):
        ans = answers.get(group)
        if ans is not None:
            try: func(ans)
            except Exception: pass
    desc = char_creator.get_character()
    await message.answer(f"Текущий персонаж: {desc or '[не выбран]'}")

@dp.message()
async def unknown_cmd(message: types.Message, state: FSMContext):
    await message.answer("Жми /start, чтобы собрать нового персонажа (хорошо подумаешь — получишь классные арты!)")

if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))