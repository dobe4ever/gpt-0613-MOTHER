import os
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils import load_json, openai_message_object, save_json


# Define the OpenAI key from the environment variable
openai.api_key = os.environ['OPENAI_API_KEY']


def run_conversation(user_message):
    user_message_dict = openai_message_object("user", user_message)
    conversation = load_json("conversation.json")
    conversation.append(user_message_dict)
    embeddings = load_json("embeddings.json")
    user_embedding = get_embedding("user", user_message)
    similar_messages = similarity_cosine(user_embedding, embeddings)
    embeddings.append(user_embedding)
    context = [conversation[0]] + similar_messages + conversation[-5:]
    print("Context: ", context)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=context, 
        temperature=1.0
    )
    ai_message = response["choices"][0]["message"]['content']
    ai_message_dict = openai_message_object("assistant", ai_message)
    ai_embedding = get_embedding("assistant", ai_message)
    conversation.append(ai_message_dict)
    embeddings.append(ai_embedding)
    save_json("conversation.json", conversation)
    save_json("embeddings.json", embeddings)
    return ai_message


def get_embedding(role, content):
    response = openai.Embedding.create(
        input=content,
        model="text-embedding-ada-002",
    )
    embedding = response['data'][0]['embedding']
    return {"role": role, "content": content, "embedding": embedding}


def similarity_cosine(embedding, embeddings):
    # Calculate cosine similarity for the new message against all history
    similarity_scores = []
    for old_embedding in embeddings:
        # Extract the content and role from the old embedding
        content = old_embedding['content']
        role = old_embedding['role']
        # Convert the old and new embeddings to numpy arrays and reshape them
        old_embedding = np.array(old_embedding['embedding']).reshape(1, -1)
        new_embedding = np.array(embedding['embedding']).reshape(1, -1)
        # Calculate the cosine similarity between the old and new embeddings
        similarity = cosine_similarity(old_embedding, new_embedding)[0][0]
        # Append the content and similarity score to the similarity scores list
        similarity_scores.append((content, similarity))
    # Sort the similarity scores in descending order
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    # Format the top 3 most similar messages as a list of dictionaries
    similar_messages = []
    for content, similarity in similarity_scores[:3]:    
        similar_messages.append({
            "role": role, 
            "content": content
        })
    # Return the list of similar messages
    return similar_messages




# def similarity_cosine(embedding, embeddings):
#     # Calculate cosine similarity for the new message against all history
#     similarity_scores = []
#     for old_embedding in embeddings:
#         content = old_embedding['content']
#         role = old_embedding['role']
#         old_embedding = np.array(old_embedding['embedding']).reshape(1, -1)
#         new_embedding = np.array(embedding['embedding']).reshape(1, -1)
#         similarity = cosine_similarity(old_embedding, new_embedding)[0][0]
#         similarity_scores.append((content, similarity))
#     # Sort the similarity scores in descending order
#     similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
#     # Print the top 5 most similar messages
#     # for content, similarity in similarity_scores[:3]:
#     #     print(f"Similarity score: {similarity:.2f}\nMessage: {content}\n")
#     # format similar messages
#     similar_messages = []
#     for content, similarity in similarity_scores[:3]:    
#         similar_messages.append({
#             "role": role, 
#             "content": content
#         })
#     return similar_messages


def transcribe_audio():
    audio_message = open("audio-message.mp3", "rb")
    transcript = openai.Audio.transcribe(
        "whisper-1",
        audio_message, 
        temperature = 0.0,
        language = "en"
    )
    return transcript['text']


def transcribe_voice():
    voice_message = open("voice-message.ogg", "rb")
    transcript = openai.Audio.transcribe(
        "whisper-1",
        voice_message, 
        temperature = 0.0,
        language = "en"
    )
    return transcript['text']


