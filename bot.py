import logging
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = '7974009937:AAFgGbCjjUzTLyhHnYVtdj-bp9_Qtw_zqH4'
HR_CHAT_ID = -4839159337

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

conn = sqlite3.connect('tsr_anketa.db')
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS lone_workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    fio TEXT,
    citizenship TEXT,
    work_permit TEXT,
    permit_validity TEXT,
    permit_regions TEXT,
    home_region TEXT,
    work_regions TEXT,
    pvc_exp TEXT,
    pvc_systems TEXT,
    al_exp TEXT,
    al_systems TEXT,
    ip_patent TEXT,
    limitations TEXT,
    limitations_details TEXT,
    conviction TEXT,
    conviction_details TEXT,
    work_10_6 TEXT,
    work_10_7 TEXT,
    objects TEXT,
    phone TEXT
);
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    contact_name TEXT,
    citizenship TEXT,
    work_permit TEXT,
    permit_validity TEXT,
    permit_regions TEXT,
    home_region TEXT,
    work_regions TEXT,
    members_count TEXT,
    max_expand TEXT,
    pvc_exp TEXT,
    pvc_systems TEXT,
    al_exp TEXT,
    al_systems TEXT,
    ip_patent TEXT,
    limitations TEXT,
    limitations_details TEXT,
    conviction TEXT,
    conviction_details TEXT,
    work_10_6 TEXT,
    work_10_7 TEXT,
    objects TEXT,
    phone TEXT
);
""")
conn.commit()

# --- Клавиатуры ---
citizenship_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="РФ")],
        [KeyboardButton(text="СНГ")],
        [KeyboardButton(text="Другое")]
    ], resize_keyboard=True, one_time_keyboard=True
)
yesno_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да")],
        [KeyboardButton(text="Нет")]
    ], resize_keyboard=True, one_time_keyboard=True
)
experience_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Нет опыта")],
        [KeyboardButton(text="<1 года")],
        [KeyboardButton(text="1–3 года")],
        [KeyboardButton(text="3–5 лет")],
        [KeyboardButton(text=">5 лет")],
        [KeyboardButton(text="Готов осваивать")]
    ], resize_keyboard=True, one_time_keyboard=True
)
ip_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Есть")],
        [KeyboardButton(text="Нет")],
        [KeyboardButton(text="Готов открыть")]
    ], resize_keyboard=True, one_time_keyboard=True
)
limitations_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Нет")],
        [KeyboardButton(text="Есть, алименты")],
        [KeyboardButton(text="Есть, кредитные задолженности")],
        [KeyboardButton(text="Есть, получаю пособия")],
        [KeyboardButton(text="Есть, другое")]
    ], resize_keyboard=True, one_time_keyboard=True
)
work_mode_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да")],
        [KeyboardButton(text="Нет")]
    ], resize_keyboard=True, one_time_keyboard=True
)
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Я монтажник (одиночка)"), KeyboardButton(text="👥 Я представляю монтажную бригаду")],
        [KeyboardButton(text="ℹ️ О компании"), KeyboardButton(text="❓ Задать вопрос")]
    ],
    resize_keyboard=True
)

user_state = {}

# ——— ФУНКЦИИ ТОЛЬКО ДЛЯ ЛИЧКИ (private) ———

@dp.message(Command('start'))
async def start(message: types.Message):
    if message.chat.type != "private":
        return
    await message.answer(
        "Добро пожаловать в бот ООО \"ТСР Остекление\"!\n"
        "Мы — производственно-монтажная компания, специализирующаяся на остеклении объектов любой сложности.\n\n"
        "⬇️ Для отклика выберите подходящий вариант:",
        reply_markup=main_kb
    )
    user_state[message.from_user.id] = None

@dp.message(lambda m: m.chat.type == "private" and m.text == "👤 Я монтажник (одиночка)")
async def lone_worker_start(message: types.Message):
    user_state[message.from_user.id] = {'role': 'lone', 'step': 1}
    await message.answer("Укажите ваши ФИО:")

@dp.message(lambda m: m.chat.type == "private" and m.text == "👥 Я представляю монтажную бригаду")
async def team_start(message: types.Message):
    user_state[message.from_user.id] = {'role': 'team', 'step': 1}
    await message.answer("ФИО контактного лица:")

@dp.message(lambda m: m.chat.type == "private" and m.text == "ℹ️ О компании")
async def about_company(message: types.Message):
    await message.answer(
        "<b>ООО “ТСР Остекление”</b> — производственно-монтажная организация, специализирующаяся на остеклении объектов любой сложности.\n\n"
        "🏢 <b>Изготавливаем и устанавливаем:</b>\n"
        "• Оконные и входные группы\n"
        "• Балконные блоки из ПВХ и алюминия\n\n"
        "🛠 <b>Что предлагаем:</b>\n"
        "• Оформление по ТК РФ (по желанию)\n"
        "• Выплаты <b>2 раза в месяц</b>\n"
        "• Бесплатный медосмотр\n"
        "• Спецодежда и инструмент\n"
        "• Занятость круглый год\n\n"
        "👷‍♂️ <b>Обязанности:</b>\n"
        "• Монтаж ПВХ и алюминиевых конструкций по проекту\n"
        "• Соблюдение охраны труда",
        parse_mode="HTML"
    )

@dp.message(lambda m: m.chat.type == "private" and m.text == "❓ Задать вопрос")
async def ask_question(message: types.Message):
    user_state[message.from_user.id] = {'role': 'question'}
    await message.answer("Пожалуйста, напишите свой вопрос. Специалист ответит вам в ближайшее время.")

@dp.message(lambda m: m.chat.type == "private" and user_state.get(m.from_user.id, {}).get('role') == 'question')
async def handle_user_question(message: types.Message):
    hr_text = (
        f"❓ Вопрос от пользователя @{message.from_user.username if message.from_user.username else message.from_user.id}:\n"
        f"{message.text}"
    )
    await bot.send_message(HR_CHAT_ID, hr_text, reply_markup=None)
    await message.answer("Ваш вопрос отправлен HR-отделу. Мы ответим вам в ближайшее время.", reply_markup=main_kb)
    user_state[message.from_user.id] = None

# Анкета для одиночки
@dp.message(lambda m: m.chat.type == "private" and user_state.get(m.from_user.id, {}).get('role') == 'lone')
async def lone_worker_form(message: types.Message):
    state = user_state[message.from_user.id]
    step = state.get('step', 1)

    if step == 1:
        state['fio'] = message.text
        await message.answer("Гражданство:", reply_markup=citizenship_kb)
        state['step'] = 2
    elif step == 2:
        state['citizenship'] = message.text
        if message.text != "РФ":
            await message.answer("Есть разрешение на проживание и работу?", reply_markup=yesno_kb)
            state['step'] = 21
        else:
            await message.answer("Регион постоянного проживания:")
            state['step'] = 3
    elif step == 21:
        state['work_permit'] = message.text
        await message.answer("Срок действия разрешения (до какого числа)?")
        state['step'] = 22
    elif step == 22:
        state['permit_validity'] = message.text
        await message.answer("В каких регионах действительно разрешение?")
        state['step'] = 23
    elif step == 23:
        state['permit_regions'] = message.text
        await message.answer("Регион постоянного проживания:")
        state['step'] = 3
    elif step == 3:
        state['home_region'] = message.text
        await message.answer("В каких регионах готовы работать?")
        state['step'] = 4
    elif step == 4:
        state['work_regions'] = message.text
        await message.answer("Опыт работы с ПВХ профильными системами:", reply_markup=experience_kb)
        state['step'] = 5
    elif step == 5:
        state['pvc_exp'] = message.text
        await message.answer("С какими профильными системами ПВХ вы работали?")
        state['step'] = 6
    elif step == 6:
        state['pvc_systems'] = message.text
        await message.answer("Опыт работы с алюминиевыми профильными системами:", reply_markup=experience_kb)
        state['step'] = 7
    elif step == 7:
        state['al_exp'] = message.text
        await message.answer("С какими профильными системами алюминия вы работали?")
        state['step'] = 8
    elif step == 8:
        state['al_systems'] = message.text
        await message.answer("Есть или готовы открыть ИП на патенте?", reply_markup=ip_kb)
        state['step'] = 9
    elif step == 9:
        state['ip_patent'] = message.text
        await message.answer("Есть ли ограничения при официальном трудоустройстве?", reply_markup=limitations_kb)
        state['step'] = 10
    elif step == 10:
        state['limitations'] = message.text
        if message.text != "Нет":
            await message.answer("Уточните, если необходимо (можно пропустить):", reply_markup=types.ReplyKeyboardRemove())
            state['step'] = 11
        else:
            state['limitations_details'] = ""
            await message.answer("Есть ли судимости?", reply_markup=yesno_kb)
            state['step'] = 12
    elif step == 11:
        state['limitations_details'] = message.text
        await message.answer("Есть ли судимости?", reply_markup=yesno_kb)
        state['step'] = 12
    elif step == 12:
        state['conviction'] = message.text
        if message.text == "Да":
            await message.answer("Уточните, если необходимо (можно пропустить):", reply_markup=types.ReplyKeyboardRemove())
            state['step'] = 13
        else:
            state['conviction_details'] = ""
            await message.answer("Готовы работать 10 ч/6 дн. в неделю?", reply_markup=work_mode_kb)
            state['step'] = 14
    elif step == 13:
        state['conviction_details'] = message.text
        await message.answer("Готовы работать 10 ч/6 дн. в неделю?", reply_markup=work_mode_kb)
        state['step'] = 14
    elif step == 14:
        state['work_10_6'] = message.text
        await message.answer("В редких случаях готовы работать 10 ч/7 дн. в неделю?", reply_markup=work_mode_kb)
        state['step'] = 15
    elif step == 15:
        state['work_10_7'] = message.text
        await message.answer("Объекты, на которых работали (название, местонахождение, объемы, виды работ):")
        state['step'] = 16
    elif step == 16:
        state['objects'] = message.text
        await message.answer("Ваш контактный телефон:")
        state['step'] = 17
    elif step == 17:
        state['phone'] = message.text

        try:
            cur.execute("""
                INSERT INTO lone_workers (
                    telegram_id, fio, citizenship, work_permit, permit_validity, permit_regions,
                    home_region, work_regions, pvc_exp, pvc_systems, al_exp, al_systems, ip_patent,
                    limitations, limitations_details, conviction, conviction_details, work_10_6, work_10_7,
                    objects, phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    message.from_user.id, state.get('fio', ""), state.get('citizenship', ""), state.get('work_permit', ""),
                    state.get('permit_validity', ""), state.get('permit_regions', ""), state.get('home_region', ""),
                    state.get('work_regions', ""), state.get('pvc_exp', ""), state.get('pvc_systems', ""), state.get('al_exp', ""),
                    state.get('al_systems', ""), state.get('ip_patent', ""), state.get('limitations', ""), state.get('limitations_details', ""),
                    state.get('conviction', ""), state.get('conviction_details', ""), state.get('work_10_6', ""),
                    state.get('work_10_7', ""), state.get('objects', ""), state.get('phone', "")
                )
            )
            conn.commit()

            hr_text = (
                f"📝 [АНКЕТА МОНТАЖНИК]\n"
                f"ФИО: {state.get('fio','')}\n"
                f"Гражданство: {state.get('citizenship','')}\n"
                f"Разрешение на работу: {state.get('work_permit','')}\n"
                f"Срок действия разрешения: {state.get('permit_validity','')}\n"
                f"Регионы действия разрешения: {state.get('permit_regions','')}\n"
                f"Регион проживания: {state.get('home_region','')}\n"
                f"Готов работать в регионах: {state.get('work_regions','')}\n"
                f"Опыт в ПВХ: {state.get('pvc_exp','')}\n"
                f"Профильные системы ПВХ: {state.get('pvc_systems','')}\n"
                f"Опыт в алюминии: {state.get('al_exp','')}\n"
                f"Профильные системы алюминия: {state.get('al_systems','')}\n"
                f"ИП на патенте: {state.get('ip_patent','')}\n"
                f"Ограничения: {state.get('limitations','')}\n"
                f"Ограничения детали: {state.get('limitations_details','')}\n"
                f"Судимости: {state.get('conviction','')}\n"
                f"Судимости детали: {state.get('conviction_details','')}\n"
                f"График 10/6: {state.get('work_10_6','')}\n"
                f"График 10/7: {state.get('work_10_7','')}\n"
                f"Объекты: {state.get('objects','')}\n"
                f"Телефон: {state.get('phone','')}\n"
                f"Telegram: @{message.from_user.username if message.from_user.username else '-'}"
            )
            await bot.send_message(HR_CHAT_ID, hr_text, reply_markup=None)
            await message.answer("Спасибо! Ваша анкета отправлена. Мы свяжемся с вами в течение 2 рабочих дней.", reply_markup=main_kb)
            user_state[message.from_user.id] = None
        except Exception as e:
            await message.answer(f"Ошибка при отправке анкеты: {e}")
            print("Ошибка при отправке анкеты:", e)

# Аналогично добавьте хендлер для бригад — ТОЛЬКО для лички:
@dp.message(lambda m: m.chat.type == "private" and user_state.get(m.from_user.id, {}).get('role') == 'team')
async def team_form(message: types.Message):
    # Логика заполнения анкеты для бригады — аналогично lone_worker_form

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
