import os
import threading
import telegram
from telegram import Bot, Update
from telegram.ext import Filters, MessageHandler, Updater
from utils import elevenlabs_gen, restart
from gpt_utils import transcribe_audio, transcribe_voice, run_conversation
from keep_alive import keep_alive, keep_alive_ping

keep_alive_ping()

# Define the Telegram bot token & user id from the environment variable
bot_token = os.environ['BOT_TOKEN']
admin_id = int(os.environ['ADMIN_ID'])
bot = Bot(token=bot_token)


def bot_send_messages(chat_id, ai_message):
    # Simulate typing action on telegram
    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    # Send text message
    bot.send_message(text=ai_message, chat_id=chat_id, parse_mode="Markdown")
    # Generate audio response
    audio_message = elevenlabs_gen(ai_message)
    # Simulate recording voice message action on telegram
    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.RECORD_AUDIO)
    # Send audio message
    bot.send_document(chat_id=chat_id, document=audio_message)


def handle_message(update, context):  
    # Get user id
    chat_id = update.message.from_user.id 
    # Get the user message
    user_message = update.message.text
    # Check if the message was sent from the specified user ID
    if chat_id == admin_id:       
        # Pass the user message to GPT & get a response
        ai_message = run_conversation(user_message)
        # Respond to user on Telegram
        bot_send_messages(chat_id, ai_message)

        restart()


def handle_voice_message(update: Update, context):
    # Get user id
    chat_id = update.message.from_user.id
    # Check if the message was sent from the specified user ID
    if chat_id == admin_id:         
        # get file id
        file_id = update.message.voice.file_id
        # get voice message
        voice_message = context.bot.get_file(file_id)
        # download voice message
        voice_message.download('voice-message.ogg')
        # Transcribe voice to text
        user_message = transcribe_voice()
        # send text message to chatGPT
        run_conversation(user_message)
        

def handle_audio_message(update: Update, context):
    # Get user id
    chat_id = update.message.from_user.id
    # Check if the message was sent from the specified user ID
    if chat_id == admin_id:
        file_id = update.message.audio.file_id
        #filename = 'audio-message.mp3'
        audio_message = context.bot.get_file(file_id)
        audio_message.download('audio-message.mp3')
        # Transcribe audio message
        user_message = transcribe_audio()
        # send text message to chatGPT
        run_conversation(user_message)

    
def main():
    # Create an instance of the Updater class using the bot token
    updater = Updater(token=bot_token, use_context=True)
    dp = updater.dispatcher

    # Create a message handler to capture voice messages
    dp.add_handler(MessageHandler(Filters.voice & ~Filters.audio, handle_voice_message))

    # Create a message handler to capture audio messages
    dp.add_handler(MessageHandler(Filters.audio & ~Filters.text, handle_audio_message))
    
    # Register the handler for all incoming messages
    dp.add_handler(MessageHandler(Filters.text, handle_message))
        
    # Start the bot
    updater.start_polling()
    
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    updater.idle()
    updater.stop()

if __name__ == '__main__':
    main()
