from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse
from pymongo import MongoClient
from datetime import datetime
from requests.structures import CaseInsensitiveDict
from openai import OpenAI
from prompts import *

from util import clean_phone_number

import tzlocal
import requests
import json

openai_client = OpenAI(
    api_key="#YOUR_API_KEY#",
)

# Constants
reverse_geocode_api_url = "https://api.geoapify.com/v1/geocode/reverse?lat={}&lon={}&apiKey=12e7ae18d88043b99a44eec809d63233"
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
local_timezone = tzlocal.get_localzone()

app = FastAPI(port=8000, host="0.0.0.0")
# Connection

MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/penpal"
DATABASE_NAME = "penpal"

client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[DATABASE_NAME]
contacts_collection = db["contacts"]
journal_collection = db["journal"]

# Server


@app.get("/")
async def root():
    return {"ping": "pong"}


@app.post("/contacts/sync/")
async def sync_contacts(request: Request):
    contacts_number_name_dict = await request.json()
    contacts_number_name_dict = dict(contacts_number_name_dict)

    contact_list = []
    for number, name in contacts_number_name_dict.items():
        number = clean_phone_number(number)

        name = str(name).strip().title()
        contact_instance = {
            "owner_email": "nateriver210@gmail.com",
            "contact_name": name,
            "phone_number": number
        }
        contact_list.append(contact_instance)

    if len(contact_list) == 0:
        return {"status": "No contacts to sync"}
    contacts_collection.delete_many(
        filter={"owner_email": "nateriver210@gmail.com"}
    )
    result = contacts_collection.insert_many(contact_list)
    inserted_ids = [str(id_) for id_ in result.inserted_ids]
    return inserted_ids


@app.post("/journal/sync/")
async def ingest_todays_general(request: Request):
    """
    request_body_format = {
      "call_logs": callEntries,
      "message_logs": messageEntries,
      "calendar_logs": calendarEntries,
      "location_logs": locationEntries,
      "usage_logs": usageStatsEntries,
    }
    """
    request_body = await request.json()
    request_body = dict(request_body)
    call_logs = request_body.get("call_logs", [])
    message_logs = request_body.get("message_logs", [])
    calendar_logs = request_body.get("calendar_logs", [])
    location_logs = request_body.get("location_logs", [])
    usage_logs = request_body.get("usage_logs", [])

    # Process call logs, convert UNIX timestamp to datetime
    for idx, call_log in enumerate(call_logs):
        call_log["timestamp"] /= 1000
        local_time = datetime.fromtimestamp(
            call_log["timestamp"], local_timezone)
        call_logs[idx]["timestamp"] = str(local_time)
        call_log["to_number"] = clean_phone_number(call_log["to_number"])
        contact_lookup = contacts_collection.find_one(
            {"phone_number": call_log["to_number"]}
        )
        if contact_lookup is not None:
            call_logs[idx]["contact_name"] = contact_lookup["contact_name"]
        else:
            call_logs[idx]["contact_name"] = "Unknown"

    # Process message logs
    for idx, message_log in enumerate(message_logs):
        message_log["to_number"] = clean_phone_number(message_log["to_number"])
        contact_lookup = contacts_collection.find_one(
            {"phone_number": message_log["to_number"]}
        )
        if contact_lookup is not None:
            message_logs[idx]["contact_name"] = contact_lookup["contact_name"]
        else:
            message_logs[idx]["contact_name"] = "Unknown"

    # Process location logs
    for idx, location_log in enumerate(location_logs):
        latitude = location_log["latitude"]
        longitude = location_log["longitude"]
        response = requests.get(
            reverse_geocode_api_url.format(latitude, longitude),
            headers=headers
        )
        response = response.json()
        location_logs[idx]["address"] = response["features"][0]["properties"]["formatted"]

    # Process usage log
    for idx, usage_log in enumerate(usage_logs):
        usage_logs[idx]["total_time_in_foreground_in_minutes"] = float(
            usage_log["total_time_in_foreground"] / 216000)

    parsed_logs = {
        "call_logs": call_logs,
        "message_logs": message_logs,
        "calendar_logs": calendar_logs,
        "location_logs": location_logs,
        "usage_logs": usage_logs,
    }

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are an actor who takes on a persona just by looking at their phone activity."},
            {"role": "user", "content": RUNNING_JOURNAL_INFERENCE_PROMPT.format(
                json.dumps(parsed_logs))}
        ]
    )
    response = str(dict(response.choices[0].message).get(
        "content", "OpenAI took long to respond. Please try again.")).strip()
    response = response.replace("[Your Name]", "Abhishek")

    return response


@app.get("/util/tts")
async def text_to_speech(text: str):
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    audio_data = response.content

    def generate():
        yield audio_data

    return StreamingResponse(
        generate(),
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=output.wav"}
    )


@app.post("/util/describe_image_and_merge_with_text/")
async def describe_image_and_merge_with_text(request: Request):
    request_body = await request.json()
    request_body = dict(request_body)
    image_url = request_body.get("image_url", "")
    text = request_body.get("text", "")

    response = openai_client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What's in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            }
        ],
    )
    image_description = dict(response.choices[0].message).get(
        "content",
        ""
    )
    print(image_description)

    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are a prolific writer who can merge any given pieces of content"},
            {"role": "user", "content": MERGE_DESC_PROMPT.format(
                text, image_description)}
        ]
    )

    return dict(response.choices[0].message).get(
        "content",
        "OpenAI took long to respond. Please try again."
    )


def read_json_and_format(file_path):
    formatted_text = ""  # Initialize formatted_text as an empty string
    with open(file_path, 'r') as file:
        data = json.load(file)
        for entry in data:
            # Use .get() to provide a default value if the key is missing
            diary_entry = entry.get("Diary Entry", "")
            timestamp = entry.get("timestamp", "")
            formatted_text += f"Timestamp: {timestamp}\nDiary Entry: {diary_entry}\n\n"
    return formatted_text


def ask_gpt_with_prompt_and_file(user_prompt, file_path):
    formatted_file_content = read_json_and_format(file_path)
    prompt_with_diary_entries = f"{user_prompt}\n\n{formatted_file_content}"

    response = openai_client.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are an actor who takes on a persona just by looking at their diary entry."},
            {"role": "user", "content": prompt_with_diary_entries},
        ]
    )
    # Handle the response as needed
    return response.choices[0].message["content"]


# Example usage
user_prompt = [
    "You are an actor who takes on a persona just by looking at their diary entry.",
    "The json is some of the diary entries I've collected about myself for over a year.",
    "Draw as many insights as you can between these data points.",
    "Try to find all kinds of correlations and links to my mood and psychological state.",
    "Given these data points, take on the persona of whomever the data points are about and chat with me going forward as if you are in his shoes in first person perspective.",
    "If you encounter any technical discrepancies or glitches while processing the data, do not mention it.",
    "Refer any names provided above only by their first name in the Journal.",
    "Make sure you don't describe the data points in the journal but tell that you have analyzed me for the past 1 year and you know me well.",
    "Start a conversation with me. Strictly do not mention a footer or the phrase The Person or the word Unknown anywhere."
]

file_path = "diary_entry.json"
