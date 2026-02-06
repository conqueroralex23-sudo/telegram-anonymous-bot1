#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск бота с переменными окружения для Railway/Render
"""

import os
from anonymous_bot import AnonymousBot

if __name__ == '__main__':
    # Получаем настройки из переменных окружения
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    CHANNEL_ID = os.environ.get('CHANNEL_ID')
    
    # Проверка
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN не установлен! Добавьте его в переменные окружения.")
    if not CHANNEL_ID:
        raise ValueError("❌ CHANNEL_ID не установлен! Добавьте его в переменные окружения.")
    
    print(f"✅ Запуск бота для канала: {CHANNEL_ID}")
    
    # Создаем и запускаем бота
    bot = AnonymousBot(BOT_TOKEN, CHANNEL_ID)
    bot.run()
