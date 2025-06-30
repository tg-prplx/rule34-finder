import os
import dotenv
import logging as log
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from charCreate import CharCreate
from r34nfag import Rule34NewForAnimeGooners

# --- INIT ---
dotenv.load_dotenv()
log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise Exception('TELEGRAM_BOT_TOKEN is missing in .env!')
bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
char_creator = CharCreate()
rule34 = Rule34NewForAnimeGooners()

# --- FSM STATE ---
class CharFSM(StatesGroup):
    step = State()
    result = State()
    wait_tags = State()

# --- STEPS ---
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

STEP_ADVICE = {
    "who":            "🧑‍🎤 <b>Тип персонажа</b>\nВыбери 1-2 типа (не всё подряд, банально = лучше результаты).",
    "body_type":      "💪 <b>Фигура</b>\nМожно пропустить, если не важно.",
    "hair_style":     "💇‍♀️ <b>Причёска</b>\nВыбери 1-2 или пропусти.",
    "hair_color":     "🎨 <b>Цвет волос</b>\nОбычный = больше артов, редкий цвета — меньше.",
    "eyes":           "👁 <b>Глаза</b>\nФорма/цвет: опционально.",
    "clothes":        "👗 <b>Одежда</b>\nНе смешивай редкое с редким — проще найти что-то банальное.",
    "pose_action":    "🕺 <b>Поза/действие</b>\nЛучше что-то простое — или ⏭️.",
    "setting":        "🏙 <b>Фон</b>\nПропускай, если фон не важен.",
    "mood":           "😊 <b>Настроение</b>\nБез разницы? Жми ⏭️.",
    "personality":    "🧠 <b>Характер</b>\nМожно смело пропускать.",
    "accessories_props": "🎒 <b>Аксессуары</b>\nОставляй пустым, если хочется увидеть больше вариантов.",
    "genre_theme":    "🌟 <b>Жанр/тема</b>\nВажен только если прям хочешь.",
    "time_weather":   "☀️ <b>Время/погода</b>\nМожно пропустить.",
    "girls":          "👧 <b>Девушки</b>\nЕсли условие обязательное.",
    "boys":           "👦 <b>Мальчики</b>\nТо же самое!"
}

# --- HELPER: Видео это? ---
def is_video_file(url: str):
    return bool(url and re.search(r'\.(mp4|webm)(\?|$)', url, re.I))

# --- Клавиатура шага ---
def build_step_keyboard(group, idx, tags, idx_selected=None, total_steps=len(func_steps)):
    max_btns = 4
    kb = []
    idx_selected = idx_selected or []
    for i, tag in enumerate(tags):
        selected = (i in idx_selected)
        btn_text = f"✅ {tag}" if selected else tag
        kb.append(InlineKeyboardButton(
            text=btn_text, callback_data=f"pick_{idx}_{i}"
        ))
    arranged = [kb[j:j + max_btns] for j in range(0, len(kb), max_btns)]
    nav1 = []
    if idx > 0:
        nav1.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{idx}"))
    nav1.append(InlineKeyboardButton(text="✅ Готово", callback_data=f"commit_{idx}"))
    nav1.append(InlineKeyboardButton(text="⏭️ Пропустить", callback_data=f"skip_{idx}"))
    if idx > 0:
        nav1.append(InlineKeyboardButton(text="🏠 К началу", callback_data="go_first"))
    nav2 = [
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
        InlineKeyboardButton(text="🗑 Очистить", callback_data=f"clear_{idx}")
    ]
    if idx < total_steps - 1:
        nav2.append(InlineKeyboardButton(text="⏩ Быстрый пропуск", callback_data="skip_all"))
    arranged.append(nav1)
    arranged.append(nav2)
    return InlineKeyboardMarkup(inline_keyboard=arranged)

# --- Вводный текст ---
async def send_intro(message):
    await message.answer(
        "👋 <b>Привет!</b> Я помогу найти арт на Rule34 по твоему описанию.\n\n"
        "🔎 На каждом шаге выбирай 1-2 признака, чтобы быстрее найти арты!\n"
        "⏩ <b>Быстрый пропуск</b> — мгновенный рандом.\n"
        "⏭️ — пропуск, если не важно. /cancel — выйти.\n"
        "🏠 — в начало, 🗑 — очистить выбор. Поехали! ⚡️",
        parse_mode="HTML")

# --- Основной шаг ---
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
                if isinstance(answer, list):
                    for a in answer:
                        func(a)
                else:
                    func(answer)
        prev_char = char_creator.get_character()
    except Exception as e:
        prev_char = f"[ошибка превью: {e}]"
    # конец
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
            await message_obj.answer("некорректный персонаж, прерываю 😭")
            await state.clear()
            return
        await message_obj.answer(
            f"🧑‍💻 <b>Готово!</b> Вот описание персонажа:\n\n<code>{desc}</code>",
            parse_mode="HTML"
        )
        posts = []
        for page in range(1, 6):
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
    group, _= func_steps[idx]
    try:
        all_tags = char_creator.get_tags()
        tags = all_tags[group]
    except Exception as e:
        await message_obj.answer(f"Ошибка загрузки вариантов для <b>{group}</b>: {e}", parse_mode="HTML")
        await state.clear()
        return
    idx_selected = answers.get(group, [])
    if idx_selected is None:
        idx_selected = []
    text = f"Шаг <b>{idx+1}/{len(func_steps)}</b> — <b>{group.replace('_', ' ').capitalize()}</b>\n"
    advice = STEP_ADVICE.get(group, "")
    if advice: text += f"{advice}\n"
    if idx_selected:
        sel_txt = ", ".join(tags[i] for i in idx_selected if 0 <= i < len(tags))
        text += f"\n<b>Выбрано:</b> <code>{sel_txt or '—'}</code>\n"
    text += "\nВыбери вариант(ы) или пропусти 👉"
    kb = build_step_keyboard(group, idx, tags, idx_selected=idx_selected, total_steps=len(func_steps))
    if preview and prev_char:
        text += f"\n\n<i>Превью:</i> <code>{prev_char or '—'}</code>"
    try:
        await message_obj.edit_text(text, parse_mode="HTML", reply_markup=kb)
        return
    except Exception:
        pass
    await message_obj.answer(text, parse_mode="HTML", reply_markup=kb)

# --- Очистить выбор ---
@dp.callback_query(F.data.startswith("clear_"))
async def clear_selection(call: CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    if len(parts) != 2: return await call.answer("ошибка!")
    idx = int(parts[1])
    data = await state.get_data()
    answers = data.get("answers", {})
    group, _= func_steps[idx]
    answers[group] = []
    await state.update_data(step_index=idx, answers=answers)
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)

# --- Мультивыбор тега ---
@dp.callback_query(F.data.startswith("pick_"))
async def pick_handler(call: CallbackQuery, state: FSMContext):
    parts = call.data.split('_')
    if len(parts) != 3: await call.answer("ошибка!"); return
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

@dp.callback_query(F.data.startswith("commit_"))
async def commit_handler(call: CallbackQuery, state: FSMContext):
    parts = call.data.split('_')
    if len(parts) != 2: await call.answer("ошибка!"); return
    idx = int(parts[1])
    await state.update_data(step_index=idx+1)
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)

# --- SKIP ---
@dp.callback_query(F.data.startswith("skip_"))
async def skip_handler(call: CallbackQuery, state: FSMContext):
    if call.data == "skip_all":
        data = await state.get_data()
        idx = data.get('step_index', 0)
        answers = data.get("answers", {})
        for i in range(idx, len(func_steps)):
            group, _= func_steps[i]
            if group not in answers:
                answers[group] = None
        await state.update_data(step_index=len(func_steps), answers=answers)
        try: await call.message.delete()
        except Exception: pass
        await send_step(call.message, state, preview=True)
        return
    parts = call.data.split("_")
    if len(parts) != 2: return await call.answer("ошибка кнопки.")
    try: idx = int(parts[1])
    except Exception: return await call.answer("ошибка кнопки.")
    data = await state.get_data()
    answers = data.get("answers", {})
    group, _= func_steps[idx]
    answers[group] = None
    await state.update_data(step_index=idx + 1, answers=answers)
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)

# --- К началу ---
@dp.callback_query(F.data == "go_first")
async def go_first_handler(call: CallbackQuery, state: FSMContext):
    await state.update_data(step_index=0)
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)

# --- prev ---
@dp.callback_query(F.data.startswith("prev_"))
async def prev_handler(call: CallbackQuery, state: FSMContext):
    parts = call.data.split('_')
    if len(parts) != 2: return await call.answer("ошибка!")
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
    await call.message.answer("создание персонажа отменено. жми /start — начнём заново!")

# --- РЕЗУЛЬТАТ ---
async def show_result(message_or_call, state: FSMContext, edit=False):
    data = await state.get_data()
    resp = data.get('result_posts', [])
    desc = data.get('result_desc', "")
    idx = data.get('result_idx', 0)
    total = len(resp)
    if not resp:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Изменить запрос", callback_data="result_edit")],
                [InlineKeyboardButton(text="❓ Советы", callback_data="help_tips")]
            ]
        )
        await send_result_message(
            message_or_call,
            "😢 <b>Картинок не найдено!</b>\n\n"
            "Попробуй упростить или убрать малопопулярные теги. Чем проще набор — тем больше шанс на успех!",
            kb, edit
        )
        return
    post = resp[idx]
    img_url = post.get("file_url") or post.get("sample_url")
    is_video = is_video_file(img_url)
    nav1 = []
    if idx > 0:
        nav1.append(InlineKeyboardButton(text='⬅️ Назад', callback_data='result_prev'))
    if idx < total - 1:
        nav1.append(InlineKeyboardButton(text='⏭️ Далее', callback_data='result_next'))
    nav2 = [
        InlineKeyboardButton(text="📝 Добавить свои теги", callback_data="result_extra_tags"),
        InlineKeyboardButton(text="✏️ Изменить запрос", callback_data="result_edit"),
        InlineKeyboardButton(text="❓ Советы", callback_data="help_tips")
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=[nav1, nav2])
    caption = (
        f"<b>Результат: {idx+1} из {total}</b>\n"
        f"<code>{desc}</code>\n"
        "\nНавигация: ⬅️/⏭️ • 📝 — добавить свои теги."
    )
    await send_result_message(message_or_call, caption, kb, edit, img_url, is_video)

async def send_result_message(message_or_call, caption, kb, edit, file_url=None, is_video=False):
    msg = message_or_call.message if isinstance(message_or_call, CallbackQuery) else message_or_call
    if not file_url:
        await msg.answer(caption, parse_mode="HTML", reply_markup=kb)
        return
    if edit:
        if is_video:
            media = types.InputMediaVideo(media=file_url, caption=caption, parse_mode="HTML")
        else:
            media = types.InputMediaPhoto(media=file_url, caption=caption, parse_mode="HTML")
        try:
            await msg.edit_media(media, reply_markup=kb)
        except Exception:
            await msg.edit_caption(caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        if is_video:
            await msg.answer_video(file_url, caption=caption, parse_mode="HTML", reply_markup=kb)
        else:
            await msg.answer_photo(file_url, caption=caption, parse_mode="HTML", reply_markup=kb)

@dp.callback_query(F.data.in_({"result_next", "result_prev"}))
async def cb_result_nav(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    idx = data.get("result_idx", 0)
    total = len(data.get('result_posts', []))
    if call.data == "result_next":
        if idx >= total - 1:
            await call.answer("последний результат")
        else:
            await state.update_data(result_idx=idx + 1)
            await call.answer()
            await show_result(call, state, edit=True)
    else:
        if idx <= 0:
            await call.answer("это первый!")
        else:
            await state.update_data(result_idx=idx - 1)
            await call.answer()
            await show_result(call, state, edit=True)

@dp.callback_query(F.data == "result_edit")
async def cb_result_edit(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    answers = data.get("answers", {})
    await state.set_state(CharFSM.step)
    await state.update_data(step_index=len(func_steps)-1, answers=answers)
    try: await call.message.delete()
    except Exception: pass
    await send_step(call.message, state, preview=True)

@dp.callback_query(F.data == "help_tips")
async def cb_help_tips(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(
        "<b>💡 Советы:</b>\n"
        "• Не выбирай слишком детально!\n"
        "• Лучшая комба — 2-3 самых важных признака.\n"
        "• Чем проще описание, тем больше артов найдётся 🌈.\n"
        "• Пробуй рандом/пропуск для экспериментов.\n",
        parse_mode="HTML"
    )
    await call.message.answer("Жми /start — собрать нового персонажа!")

@dp.callback_query(F.data == "result_extra_tags")
async def cb_result_extra_tags(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(CharFSM.wait_tags)
    await call.message.answer(
        "✍️ <b>Впиши дополнительные теги (через пробел, без лишних знаков):</b>\n"
        "<i>Например: blue_eyes smile outdoor</i>",
        parse_mode="HTML"
    )

@dp.message(CharFSM.wait_tags)
async def msg_extra_tags(message: types.Message, state: FSMContext):
    data = await state.get_data()
    extra_tags = message.text.strip()
    if not extra_tags:
        await message.answer("Пусто. Попробуй снова или /cancel.")
        return
    char_creator.char = ""
    answers = data.get('answers', {})
    for i, (group, func) in enumerate(func_steps):
        ans = answers.get(group)
        if ans is not None:
            if isinstance(ans, list):
                for a in ans:
                    func(a)
            else:
                func(ans)
    char_creator.char += " " + extra_tags
    desc = char_creator.get_character()
    posts = []
    for page in range(1, 6):
        chunk = rule34.make_rule34_request(desc, pid=page-1, limit=10)
        if not isinstance(chunk, list) or not chunk:
            break
        posts.extend(chunk)
        if len(posts) >= 50:
            break
    posts = posts[:50]
    await state.set_state(CharFSM.result)
    await state.update_data(result_posts=posts, result_desc=desc, result_idx=0)
    await message.answer(f"✅ Обновлено с тегами: <code>{extra_tags}</code>", parse_mode="HTML")
    await show_result(message, state)

# --- КОМАНДЫ ---
@dp.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(CharFSM.step)
    await state.update_data(step_index=0, answers={})
    await send_intro(message)
    await send_step(message, state, preview=True)

@dp.message(Command('reset'))
async def cmd_reset(message: types.Message, state: FSMContext):
    await state.clear()
    await cmd_start(message, state)

@dp.message(Command('cancel'))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("создание персонажа отменено. жми /start — снова попробуем!")

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
    await message.answer(f"📝 <b>текущее описание:</b> <code>{desc or '[ничего не выбрано]'}</code>", parse_mode="HTML")

@dp.message(Command('help'))
async def cmd_help(message: types.Message, state: FSMContext):
    await message.answer(
        "⚡️ <b>Справка по боту:</b>\n"
        "1. Не выбирай ВСЁ подряд — будет мало картинок!\n"
        "2. Чем проще — тем больше артов (фичи типа цвет волос, одежда, поза — важны!)\n"
        "3. Попробуй разные комбинации, если нет результата.\n"
        "4. На любом шаге тыкай <b>⏩ Быстрый пропуск</b>, если лень.\n\n"
        "/start — начать заново\n"
        "/reset — сброс\n"
        "/help — ещё раз эту подсказку\n"
        "/cancel — выйти 🦋",
        parse_mode="HTML"
    )

@dp.message()
async def unknown_cmd(message: types.Message, state: FSMContext):
    await message.answer("🚦 не знаю такой команды. жми /start чтобы собрать нового персонажа! шагай по кнопкам и наслаждайся артом! 🌈")

# --- СТАРТ ПОЛЛИНГА ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))