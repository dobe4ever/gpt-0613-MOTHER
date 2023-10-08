import json
from elevenlabs import generate
from datetime import datetime
import pytz


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, file):
    with open(path, "w") as f:
        f.write(json.dumps(file, indent=4))

def openai_message_object(role, content):
    content = f"{get_timestamp()}{content}"
    return {
        "role": role, 
        "content": content
    }


def get_timestamp():
    # Obtain the Bangkok timezone
    madrid_timezone = pytz.timezone('Asia/Bangkok')
    # Obtain the current date and time in Bangkok
    now = datetime.now(madrid_timezone)
    timestamp = now.strftime("%A, %d-%m-%Y at %H:%M - ")
    return timestamp


def elevenlabs_gen(ai_message):
    # Optimize text message for speech
    paragraphs = split_text(text=ai_message)
    # Convert text to audio & save the file
    generate_audio(paragraphs)
    return open('audio-response.mp3', 'rb')

        
def calculate_token_cost(response_data):
    # Access necessary data from the response_data
    model = response_data['model']
    usage = response_data['usage']
    
    if model == "gpt-3.5-turbo-0613":
        # Price for "gpt-3.5-turbo-0613"
        prompt_cost_per_k_tokens = 0.0015  
        completion_cost_per_k_tokens = 0.002 

    elif model == "gpt-4-0613":
        # Price for "gpt-4-0613"
        prompt_cost_per_k_tokens = 0.03
        completion_cost_per_k_tokens = 0.06
    else:
        print("Cannot calculate cost: Model not found")
        return
        
    prompt_tokens = usage["prompt_tokens"]
    completion_tokens = usage["completion_tokens"]
    # total_tokens = usage["total_tokens"]

    prompt_cost = (prompt_tokens / 1000) * prompt_cost_per_k_tokens
    completion_cost = (completion_tokens / 1000) * completion_cost_per_k_tokens

    total_cost = prompt_cost + completion_cost
    
    # format for readablility
    prompt_cost = "{:.8f}".format(prompt_cost)
    completion_cost = "{:.8f}".format(completion_cost)
    total_cost = "{:.8f}".format(total_cost)

    return total_cost


def split_text(text):
    # Split the text into chunks of 2400 characters each
    chunks = [text[i:i+2400] for i in range(0, len(text), 2400)]
    
    paragraphs = []
    
    for chunk in chunks:
        start = 0
        while start < len(chunk):
            # Find the closest period before the 230th character
            end = chunk.rfind('.', start, start + 230)
            
            if end == -1: 
                # If there is no period within the first 230 characters,
                # just cut off at the maximum length.
                end = min(start + 230, len(chunk))
                
            paragraph = chunk[start:end].strip()
            
            if paragraph: 
                paragraphs.append(paragraph)
                
            start = end + 1
            
    return paragraphs


def generate_audio(paragraphs):
    audio_files = []

    for paragraph in paragraphs:
        print(paragraph, "\n\n")
 
        # Generate audio for each paragraph
        audio = generate(
            text=paragraph,
            voice='Bella',
            # api_key="",
        )
        audio_files.append(audio)

    # Combine all audios into one and save it
    combined_audio = b"".join(audio_files)
    
    with open("audio-response.mp3", "wb") as f:
        f.write(combined_audio)


def restart():
    import subprocess
    SystemExit()
    # Reset container
    subprocess.run(["kill", "1"])


