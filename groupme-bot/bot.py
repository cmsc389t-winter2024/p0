import requests
import time
import json
import os
from dotenv import load_dotenv
import requests
from urllib.parse import urlencode 
import re

load_dotenv()

BOT_ID = os.getenv("BOT_ID")
GROUP_ID = os.getenv("GROUP_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
LAST_MESSAGE_ID = None
MY_USER_ID = "94000657"
BASE_URL = 'https://api.planetterp.com/v1/'


def send_message(text, attachments=None):
    """Send a message to the group using the bot."""
    post_url = "https://api.groupme.com/v3/bots/post"
    data = {"bot_id": BOT_ID, "text": text, "attachments": attachments or []}
    response = requests.post(post_url, json=data)
    return response.status_code == 202


def get_group_messages(since_id=None):
    """Retrieve recent messages from the group."""
    params = {"token": ACCESS_TOKEN}
    if since_id:
        params["since_id"] = since_id
    get_url = f"https://api.groupme.com/v3/groups/{GROUP_ID}/messages"
    response = requests.get(get_url, params=params)
    if response.status_code == 200:
        # this shows how to use the .get() method to get specifically the messages but there is more you can do (hint: sample.json)
        return response.json().get("response", {}).get("messages", [])
    return []


def process_message(message):
    global LAST_MESSAGE_ID
    sender_id = message["sender_id"]
    sender_name = message["name"]

    # TASK 1: respond to you
    if sender_id == MY_USER_ID:
        send_message(f"Hi, {sender_name}!")

    
    if sender_id != "system":
        text = message["text"].lower()
        # TASK 2: good morning/good night
        if "good morning" in text:
            send_message(f"Good morning, {sender_name}!")
        elif "good night" in text:
            send_message(f"Good night, {sender_name}!")

        # TASK 3: create 1 (or more, for extra-credit) additional features that you think would be cool
        else:
            pattern = r"bot, can you give me the average gpa in ([a-z]{4}\d{3}[a-z]) with professor (.+)"
            match = re.match(pattern, text)
            if match:
                course = match.group(1)
                professor = match.group(2)
                params = {"course" : course, "professor": professor}
                params = {k:v for k, v in params.items() if v is not None}
                url = BASE_URL + "grades?" + urlencode(params)
                grade_data = requests.get(url).json()
                avg_GPA = round(calculate_average_gpa(grade_data), 2)
                send_message(f"Sure! Heres the Average GPA of {course} with Professor {professor}: {avg_GPA}!")
    LAST_MESSAGE_ID = message["id"]


def calculate_average_gpa(grades_data):
    gpa_values = {"A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0}
    total_gpa = 0
    total_students = 0
    for record in grades_data:
        for grade, count in record.items():
            if grade in gpa_values:
                total_gpa += gpa_values[grade] * count
                total_students += count
    return total_gpa / total_students if total_students > 0 else 0


def main():
    global LAST_MESSAGE_ID
    # this is an infinite loop that will try to read (potentially) new messages every 10 seconds, but you can change this to run only once or whatever you want
    while True:
        messages = get_group_messages(LAST_MESSAGE_ID)
        for message in reversed(messages):
            process_message(message)
        time.sleep(10)

if __name__ == "__main__":
    main()