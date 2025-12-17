import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ===== ЛОГИРОВАНИЕ =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== ИНИЦИАЛИЗАЦИЯ OPENROUTER КЛИЕНТА =====
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Выберите модель (примеры доступных моделей)
# "deepseek/deepseek-chat" - DeepSeek
# "meta-llama/llama-3.1-8b-instruct:free" - Llama 3.1 (бесплатная)
# "google/gemini-2.0-flash-exp:free" - Gemini 2.0 Flash (бесплатная)
# "anthropic/claude-3.5-sonnet" - Claude 3.5
# "openai/gpt-4o-mini" - GPT-4o Mini

MODEL = "deepseek/deepseek-chat"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик сообщений с командой !гпт"""
    
    message_text = update.message.text
    
    # Проверяем, начинается ли сообщение с !гпт
    if not message_text.lower().startswith("!гпт"):
        return
    
    # Извлекаем вопрос
    question = message_text[4:].strip()
    
    # Проверяем, есть ли вопрос
    if not question:
        await update.message.reply_text(
            "❌ Укажите вопрос после команды.\n"
            "Пример: `!гпт Как работает Python?`",
            parse_mode='Markdown'
        )
        return
    
    # Индикатор "печатает..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action="typing"
    )
    
    try:
        # Запрос к OpenRouter API
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "Ты полезный ассистент. Отвечай на русском языке."
                },
                {
                    "role": "user", 
                    "content": question
                }
            ],
            max_tokens=2048,
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": "https://your-site.com",  # Опционально
                "X-Title": "Telegram Bot"                  # Опционально
            }
        )
        
        # Получаем ответ
        answer = response.choices[0].message.content
        
        # Разбиваем длинные сообщения (лимит Telegram - 4096 символов)
        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                await update.message.reply_text(answer[i:i+4000])
        else:
            await update.message.reply_text(answer)
        
        logger.info(f"✅ Вопрос обработан | Модель: {MODEL}")
        
    except Exception as e:
        logger.error(f"Ошибка API: {e}")
        await update.message.reply_text(
            f"⚠️ Ошибка при обращении к API:\n`{str(e)[:300]}`",
            parse_mode='Markdown'
        )


def main() -> None:
    """Запуск бота"""
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    logger.info(f"🚀 Бот запущен! Модель: {MODEL}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
