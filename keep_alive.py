from flask import Flask
from threading import Thread
import requests
import os
from datetime import datetime
import time


bot_token = os.environ['BOT_TOKEN']


app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive"

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive_ping():
    t = Thread(target=run)
    t.start()



def keep_alive():
    while True:
        response = requests.get(f'https://api.telegram.org/bot{bot_token}/getMe')
        print("Keep-alive executed at", datetime.now(), "status code:", response.status_code)
        print("Response status code:", response.status_code)
        print("Response content:", response.content)
        time.sleep(600)  # Delay execution for 10 minute
