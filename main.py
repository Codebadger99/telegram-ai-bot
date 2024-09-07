import telebot
import google.generativeai as genai
import time
import os
from dotenv import load_dotenv

load_dotenv()


bot = telebot.TeleBot(os.getenv('TELEGRAM_API_KEY'), parse_mode=None)
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

model = genai.GenerativeModel(
    "gemini-1.5-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

chat = model.start_chat(
    history=[
        {"role": "user", "parts": "Hello"},
        {"role": "model", "parts": "Great to meet you. What would you like to know?"},
    ]
)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if message.content_type == "text":
        # Extract the user's message text
        user_message = message.text

        # Send the user's message to the chat model
        chat.send_message({"role": "user", "parts": user_message})

        # Fetch the model's response
        response = chat.last.text

        bot.send_chat_action(message.chat.id, "typing")

        time.sleep(2)

        # Send the model's response back to the user
        bot.reply_to(message, response)
    else:
        bot.send_message(message.chat.id, "I can only handle text messages right now.")


bot.infinity_polling()
