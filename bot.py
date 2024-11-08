from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
from config import BOT_TOKEN  # Импортируем токен из config.py
import re
from datetime import time
from collections import defaultdict
from pytz import timezone

# Словарь для хранения статистики отправленных ссылок и лайков
link_statistics = defaultdict(int)
like_statistics = defaultdict(int)

async def modify_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем текст сообщения
    message_text = update.message.text

    # Проверяем, содержит ли сообщение ссылку, начинающуюся с "https://www."
    if "instagram" in message_text:
        # Модифицируем текст сообщения, добавляя "dd" после "www."
        modified_text = re.sub(r'instagram', 'ddinstagram', message_text)

        # Получаем информацию о пользователе
        user = update.message.from_user
        user_username = f"@{user.username}" if user.username else ""
        display_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

        # Заменяем имя пользователя по указанным правилам
        if user.username == "semenovanadejda":
            display_name = "РСП"
        elif user.username == "N1CE4RT":
            display_name = "Гений, миллиардер, плейбой, филантроп отправляет"
        elif user.username == "Vikki_Streltsova_04":
            display_name = "Шиншилина"

        # Добавляем изменённое имя пользователя после ссылки
        modified_text += f"\n\n{user_username} {display_name} отправляет"

        # Обновляем статистику ссылок
        link_statistics[user_username] += 1

        # Удаляем исходное сообщение
        await update.message.delete()

        # Создаем кнопку "лайк"
        keyboard = [[InlineKeyboardButton("❤️", callback_data=f"like|{user_username}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем новое сообщение с модифицированной ссылкой и кнопкой "лайк"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=modified_text,
            reply_markup=reply_markup
        )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Получаем информацию о пользователе из callback_data
    action, user_username = query.data.split("|")
    if action == "like":
        like_statistics[user_username] += 1

async def send_daily_statistics(context: CallbackContext):
    chat_id = context.job.data  # Указываем чат, куда отправлять статистику
    print("Функция отправки статистики запущена")  # Отладка
    if link_statistics or like_statistics:
        stats_message = "Статистика за сегодняшний день:\n"
        all_users = set(link_statistics.keys()).union(like_statistics.keys())
        for user in all_users:
            videos = link_statistics[user]
            likes = like_statistics[user]
            stats_message += f"{user} отправил(а) {videos} видео, суммарное количество лайков: {likes}\n"

        # Отправляем сообщение со статистикой
        await context.bot.send_message(chat_id=chat_id, text=stats_message)
        print("Статистика отправлена")  # Отладка

        # Очищаем статистику для нового дня
        link_statistics.clear()
        like_statistics.clear()
    else:
        await context.bot.send_message(chat_id=chat_id, text="Статистика за сегодняшний день: нет отправленных видео и лайков.")
        print("Сообщение о пустой статистике отправлено")  # Отладка

# Инициализация приложения
app = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(token=BOT_TOKEN)

# Обработчик текстовых сообщений
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, modify_message))

# Обработчик нажатий кнопок
app.add_handler(CallbackQueryHandler(button_click))

# Настройка задания для отправки ежедневной статистики в 23:59
job_queue = app.job_queue
job_queue.run_daily(send_daily_statistics, time(hour=23, minute=59, tzinfo=timezone('Europe/Moscow')), data='-4509646495')

# Запуск бота
app.run_polling()


