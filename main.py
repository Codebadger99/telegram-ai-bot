import telebot
import google.generativeai as genai
import time
import os
from dotenv import load_dotenv
from google.auth.exceptions import TransportError

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_API_KEY'), parse_mode=None)

# Configure Google Generative AI with API key from environment variables
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
except TransportError as e:
    print(f"Error configuring Generative AI: {e}")
    genai = None  # Set genai to None if configuration fails

# Define generation settings and safety settings
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

try:
    # Initialize the generative model
    model = genai.GenerativeModel(
        "gemini-1.5-pro",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )

    # Start a chat session with predefined history
    chat = model.start_chat(
        history=[
            {"role": "user", "parts": "Hello"},
            {"role": "model", "parts": "Great to meet you. What would you like to know?"},
        ]
    )
except TransportError as e:
    print(f"Error initializing Generative Model or starting chat: {e}")
    chat = None  # Set chat to None if initialization fails

# Define bot command handler for /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

# Define bot message handler for all messages
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if message.content_type == "text":
        # Extract the user's message text
        user_message = message.text

        if chat is None:
            bot.reply_to(message, "Service is temporarily unavailable. Please try again later.")
            return

        try:
            # Send the user's message to the chat model
            chat.send_message({"role": "user", "parts": user_message})

            # Fetch the model's response
            response = chat.last.text

            # Simulate typing action
            bot.send_chat_action(message.chat.id, "typing")
            time.sleep(2)

            # Send the model's response back to the user
            bot.reply_to(message, response)

        except TransportError as e:
            print(f"TransportError occurred: {e}")
            bot.reply_to(message, "An error occurred while processing your request. Please try again later.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            bot.reply_to(message, "An unexpected error occurred. Please contact support.")
    else:
        bot.send_message(message.chat.id, "I can only handle text messages right now.")

# Start the bot with infinity polling
if __name__ == "__main__":
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"An error occurred while starting the bot: {e}")
