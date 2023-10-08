import json
import os
import openai
from docx import Document
from langdetect import detect


# Define the OpenAI key from the environment variable
openai.api_key = os.environ['OPENAI_API_KEY']


def run_conversation(user_message):
    # Load conversation history
    with open("conversation.json", "r") as f:
        conversation = json.load(f)
    # Define conversation context
    conversation_context = [conversation[0]] + conversation[-10:]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_context, 
        temperature=0.0
    )
    return response["choices"][0]["message"]['content']


def transcribe_audio():
    audio_message = open("audio-message.mp3", "rb")
    transcript = openai.Audio.transcribe(
        "whisper-1",
        audio_message, 
        temperature = 0.0,
        language = "th"
    )
    transcript = transcript['text']
    # Detect the language of the transcript
    language = detect(transcript)
    if language == 'th':
        return f"Below is a transcript from some audio recording in Thai. What does it mean?\n\n{transcript}"
    else: 
        return transcript


def transcribe_voice():
    voice_message = open("voice-message.ogg", "rb")
    transcript = openai.Audio.transcribe(
        "whisper-1",
        voice_message, 
        temperature = 0.0,
    )
    transcript = transcript['text']
    # Detect the language of the transcript
    language = detect(transcript)
    if language == 'th':
        return f"Below is a transcript from some audio recording in Thai. What does it mean?\n\n{transcript}"
    else: 
        return transcript
  




