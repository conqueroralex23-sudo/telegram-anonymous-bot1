#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенная версия бота с конфигурацией из config.py
"""

from anonymous_bot import AnonymousBot
from config import BOT_TOKEN, CHANNEL_ID

if __name__ == '__main__':
    # Создание и запуск бота
    bot = AnonymousBot(BOT_TOKEN, CHANNEL_ID)
    bot.run()
