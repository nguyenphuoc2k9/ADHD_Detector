from dotenv import load_dotenv,find_dotenv
import os
load_dotenv(find_dotenv("BE/.env"))
API_KEY = os.environ.get("GEMINI_API_KEY")
print(API_KEY)
from google import genai
client = genai.Client(api_key=API_KEY)
chat = client.chats.create(model="gemini-2.5-flash")
def ask_AI(user_chat,timestamp,time='day'):
    prompt = f"""
    You are a helpful productivity advisor.
    The user is a student who is trying to improve focus and study habits.
    Below is their focus_score history for the past {time}.

    focus_history = {timestamp}

    Requirements:
    - Analyze daily patterns (high/low focus times)
    - Identify possible causes: fatigue, distractions, irregular routines
    - Provide **safe and age-appropriate** suggestions such as:
      - study timing
      - breaks
      - planning strategies
      - workspace improvements
      - motivation techniques
    - Keep tone supportive, positive, and not judgmental.
    - DO NOT reference anything medical or harmful.
    - DO NOT mention self-harm, depression, or anything sensitive.
    - Answer in less than 100 word
    - Answer the question of user accordingly and don't suggest anymore plan unless the user demanded so.
    Give a practical study plan for tomorrow and some general advice based on the pattern.
    Here is user text:
    User: {user_chat}
    """
    res = chat.send_message(prompt)
    return {'ai_chat':res.text}
