#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анонимный Telegram бот для отправки сообщений в канал
Автор: Адаптировано для пользователя
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
import json
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для состояний разговора
CHOOSING_NICKNAME, WAITING_MESSAGE = range(2)

# Файл для хранения данных пользователей
USER_DATA_FILE = 'user_data.json'
STATS_FILE = 'stats.json'


class AnonymousBot:
    def __init__(self, bot_token, channel_id):
        """
        Инициализация бота
        
        Args:
            bot_token (str): Токен бота от BotFather
            channel_id (str): ID канала для публикации (например: @your_channel или -100...)
        """
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.user_data = self.load_user_data()
        self.stats = self.load_stats()
        
    def load_user_data(self):
        """Загрузка данных пользователей из файла"""
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_user_data(self):
        """Сохранение данных пользователей в файл"""
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=2)
    
    def load_stats(self):
        """Загрузка статистики"""
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'total_messages': 0, 'total_users': 0}
    
    def save_stats(self):
        """Сохранение статистики"""
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def get_user_nickname(self, user_id):
        """Получить никнейм пользователя"""
        user_id_str = str(user_id)
        if user_id_str in self.user_data:
            return self.user_data[user_id_str].get('nickname')
        return None
    
    def set_user_nickname(self, user_id, nickname):
        """Установить никнейм пользователя"""
        user_id_str = str(user_id)
        if user_id_str not in self.user_data:
            self.user_data[user_id_str] = {}
            self.stats['total_users'] = len(self.user_data)
        
        self.user_data[user_id_str]['nickname'] = nickname
        self.user_data[user_id_str]['created_at'] = datetime.now().isoformat()
        self.save_user_data()
        self.save_stats()
    
    def get_next_message_number(self):
        """Получить номер следующего сообщения"""
        self.stats['total_messages'] += 1
        self.save_stats()
        return self.stats['total_messages']

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        user_id = user.id
        
        nickname = self.get_user_nickname(user_id)
        
        welcome_text = (
            f"👋 Привет, {user.first_name}!\n\n"
            f"🎭 Это анонимный бот для отправки сообщений в канал.\n\n"
        )
        
        if nickname:
            welcome_text += (
                f"✅ Ваш текущий никнейм: <b>{nickname}</b>\n\n"
                f"📝 Просто отправьте мне сообщение, и оно будет опубликовано в канале от вашего имени.\n\n"
                f"🔄 Команды:\n"
                f"/change_nickname - Изменить никнейм\n"
                f"/remove_nickname - Удалить никнейм (сообщения будут с номером)\n"
                f"/stats - Посмотреть статистику\n"
                f"/help - Помощь"
            )
            await update.message.reply_text(welcome_text, parse_mode='HTML')
        else:
            welcome_text += (
                f"🎯 Выберите, как хотите отправлять сообщения:\n\n"
                f"1️⃣ С личным никнеймом\n"
                f"2️⃣ Под номером сообщения (анонимно)"
            )
            
            keyboard = [
                [KeyboardButton("✏️ Установить никнейм")],
                [KeyboardButton("🔢 Отправлять под номером")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            
            await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')
            return CHOOSING_NICKNAME

    async def choose_nickname_option(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора опции никнейма"""
        text = update.message.text
        
        if text == "🔢 Отправлять под номером":
            await update.message.reply_text(
                "✅ Отлично! Ваши сообщения будут публиковаться под номером.\n\n"
                "📝 Отправьте мне любое сообщение, и оно появится в канале!",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        
        elif text == "✏️ Установить никнейм":
            await update.message.reply_text(
                "✏️ Введите ваш никнейм:\n\n"
                "⚠️ Никнейм должен быть от 2 до 20 символов.\n"
                "Можно использовать буквы, цифры и символ _",
                reply_markup=ReplyKeyboardRemove()
            )
            return WAITING_MESSAGE
        
        return ConversationHandler.END

    async def set_nickname(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установка никнейма пользователя"""
        nickname = update.message.text.strip()
        user_id = update.effective_user.id
        
        # Валидация никнейма
        if len(nickname) < 2 or len(nickname) > 20:
            await update.message.reply_text(
                "❌ Никнейм должен быть от 2 до 20 символов. Попробуйте еще раз:"
            )
            return WAITING_MESSAGE
        
        if not all(c.isalnum() or c == '_' for c in nickname):
            await update.message.reply_text(
                "❌ Никнейм может содержать только буквы, цифры и символ _. Попробуйте еще раз:"
            )
            return WAITING_MESSAGE
        
        # Сохранение никнейма
        self.set_user_nickname(user_id, nickname)
        
        await update.message.reply_text(
            f"✅ Отлично! Ваш никнейм установлен: <b>{nickname}</b>\n\n"
            f"📝 Теперь отправьте мне сообщение, и оно будет опубликовано в канале от вашего имени!\n\n"
            f"💡 Вы всегда можете изменить никнейм командой /change_nickname",
            parse_mode='HTML'
        )
        return ConversationHandler.END

    async def change_nickname_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для изменения никнейма"""
        await update.message.reply_text(
            "✏️ Введите новый никнейм:\n\n"
            "⚠️ Никнейм должен быть от 2 до 20 символов.\n"
            "Можно использовать буквы, цифры и символ _"
        )
        return WAITING_MESSAGE

    async def remove_nickname_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление никнейма пользователя"""
        user_id = update.effective_user.id
        user_id_str = str(user_id)
        
        if user_id_str in self.user_data and 'nickname' in self.user_data[user_id_str]:
            del self.user_data[user_id_str]['nickname']
            self.save_user_data()
            await update.message.reply_text(
                "✅ Ваш никнейм удален.\n\n"
                "📝 Теперь ваши сообщения будут публиковаться под номером."
            )
        else:
            await update.message.reply_text(
                "ℹ️ У вас нет установленного никнейма.\n\n"
                "Используйте /start для настройки."
            )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать статистику"""
        user_id = update.effective_user.id
        nickname = self.get_user_nickname(user_id)
        
        stats_text = (
            f"📊 <b>Статистика бота:</b>\n\n"
            f"📝 Всего сообщений: {self.stats['total_messages']}\n"
            f"👥 Всего пользователей: {self.stats['total_users']}\n\n"
        )
        
        if nickname:
            stats_text += f"🎭 Ваш никнейм: <b>{nickname}</b>"
        else:
            stats_text += f"🔢 Вы отправляете сообщения под номером"
        
        await update.message.reply_text(stats_text, parse_mode='HTML')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать помощь"""
        help_text = (
            "📖 <b>Помощь по использованию бота:</b>\n\n"
            "🎭 <b>Как это работает?</b>\n"
            "Отправьте мне любое сообщение (текст, фото, видео), и оно будет анонимно опубликовано в канале.\n\n"
            "🔤 <b>Никнейм или номер?</b>\n"
            "• С никнеймом - ваши сообщения будут подписаны вашим именем\n"
            "• Под номером - сообщения будут подписаны как 'Сплетня #123'\n\n"
            "⚙️ <b>Доступные команды:</b>\n"
            "/start - Начать работу с ботом\n"
            "/change_nickname - Изменить никнейм\n"
            "/remove_nickname - Удалить никнейм\n"
            "/stats - Статистика\n"
            "/help - Эта справка\n\n"
            "💬 <b>Поддерживаемые типы сообщений:</b>\n"
            "• Текст\n"
            "• Фото\n"
            "• Видео\n"
            "• Аудио\n"
            "• Документы\n"
            "• Голосовые сообщения"
        )
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка обычных сообщений и отправка в канал"""
        user_id = update.effective_user.id
        nickname = self.get_user_nickname(user_id)
        message_number = self.get_next_message_number()
        
        # Формирование подписи
        if nickname:
            signature = f"✍️ От: <b>{nickname}</b>"
        else:
            signature = f"🔢 Сплетня #{message_number}"
        
        try:
            # Обработка разных типов сообщений
            if update.message.text:
                # Текстовое сообщение
                full_message = f"{update.message.text}\n\n{signature}"
                await context.bot.send_message(
                    chat_id=self.channel_id,
                    text=full_message,
                    parse_mode='HTML'
                )
            
            elif update.message.photo:
                # Фото
                photo = update.message.photo[-1]  # Берем фото лучшего качества
                caption = update.message.caption or ""
                full_caption = f"{caption}\n\n{signature}" if caption else signature
                await context.bot.send_photo(
                    chat_id=self.channel_id,
                    photo=photo.file_id,
                    caption=full_caption,
                    parse_mode='HTML'
                )
            
            elif update.message.video:
                # Видео
                caption = update.message.caption or ""
                full_caption = f"{caption}\n\n{signature}" if caption else signature
                await context.bot.send_video(
                    chat_id=self.channel_id,
                    video=update.message.video.file_id,
                    caption=full_caption,
                    parse_mode='HTML'
                )
            
            elif update.message.audio:
                # Аудио
                caption = update.message.caption or ""
                full_caption = f"{caption}\n\n{signature}" if caption else signature
                await context.bot.send_audio(
                    chat_id=self.channel_id,
                    audio=update.message.audio.file_id,
                    caption=full_caption,
                    parse_mode='HTML'
                )
            
            elif update.message.voice:
                # Голосовое сообщение
                await context.bot.send_voice(
                    chat_id=self.channel_id,
                    voice=update.message.voice.file_id,
                    caption=signature,
                    parse_mode='HTML'
                )
            
            elif update.message.document:
                # Документ
                caption = update.message.caption or ""
                full_caption = f"{caption}\n\n{signature}" if caption else signature
                await context.bot.send_document(
                    chat_id=self.channel_id,
                    document=update.message.document.file_id,
                    caption=full_caption,
                    parse_mode='HTML'
                )
            
            # Подтверждение отправки
            await update.message.reply_text(
                "✅ Ваше сообщение опубликовано в канале!\n\n"
                f"📊 Сообщение #{message_number}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в канал: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при публикации сообщения.\n\n"
                "⚠️ Убедитесь, что бот добавлен в канал как администратор с правом публикации сообщений."
            )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена операции"""
        await update.message.reply_text(
            "❌ Действие отменено.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def run(self):
        """Запуск бота"""
        # Создание приложения
        application = Application.builder().token(self.bot_token).build()
        
        # ConversationHandler для установки никнейма
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_command)],
            states={
                CHOOSING_NICKNAME: [
                    MessageHandler(
                        filters.Regex('^(✏️ Установить никнейм|🔢 Отправлять под номером)$'),
                        self.choose_nickname_option
                    )
                ],
                WAITING_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.set_nickname)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
        
        # ConversationHandler для изменения никнейма
        change_nickname_handler = ConversationHandler(
            entry_points=[CommandHandler('change_nickname', self.change_nickname_command)],
            states={
                WAITING_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.set_nickname)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
        
        # Добавление обработчиков
        application.add_handler(conv_handler)
        application.add_handler(change_nickname_handler)
        application.add_handler(CommandHandler('remove_nickname', self.remove_nickname_command))
        application.add_handler(CommandHandler('stats', self.stats_command))
        application.add_handler(CommandHandler('help', self.help_command))
        
        # Обработчик всех сообщений (текст, фото, видео и т.д.)
        application.add_handler(MessageHandler(
            filters.ALL & ~filters.COMMAND,
            self.handle_message
        ))
        
        # Запуск бота
        logger.info("Бот запущен!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    # ВАЖНО: Замените эти значения на свои!
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Токен от @BotFather
    CHANNEL_ID = "@your_channel"  # ID или username вашего канала (например: @mychannel или -1001234567890)
    
    # Создание и запуск бота
    bot = AnonymousBot(BOT_TOKEN, CHANNEL_ID)
    bot.run()
