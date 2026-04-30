import json
import os
import re

MEMORY_FILE = "data/user_memory.json"

def delete_chat(memory, chat_id):
    memory["chats"] = [c for c in memory["chats"] if c["id"] != chat_id]

    # if deleted chat was active → switch to another
    if memory["current_chat_id"] == chat_id:
        if memory["chats"]:
            memory["current_chat_id"] = memory["chats"][0]["id"]
        else:
            # create new empty chat
            new_chat = {"id": 1, "messages": []}
            memory["chats"] = [new_chat]
            memory["current_chat_id"] = 1

    return memory

def get_current_chat(memory):
    if not memory.get("chats"):
        return None

    for chat in memory["chats"]:
        if chat["id"] == memory.get("current_chat_id"):
            return chat

    # 🔥 fallback if id not found
    return memory["chats"][0]


def create_new_chat(memory):
    if memory["chats"]:
        max_id = max(chat["id"] for chat in memory["chats"])
        new_id = max_id + 1
    else:
        new_id = 1

    new_chat = {
        "id": new_id,
        "messages": []
    }

    memory["chats"].append(new_chat)
    memory["current_chat_id"] = new_id

    return memory


def switch_chat(memory, chat_id):
    memory["current_chat_id"] = chat_id
    return memory

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"current_chat": [], "profile": {}}
    
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    os.makedirs("data", exist_ok=True)  # 🔥 creates folder if not exists
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def update_profile(user_input, profile):
    user_input_lower = user_input.lower()

    # 💰 income
    income_match = re.search(r'(\d{4,6})', user_input)
    if "earn" in user_input_lower and income_match:
        profile["income"] = int(income_match.group(1))

    # 🎯 goal
    if "buy" in user_input_lower:
        profile["goal"] = user_input

    # 💸 saving intent
    if "save" in user_input_lower:
        profile["saving_intent"] = True

    return profile