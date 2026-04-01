# Store/change/get json data (quiz, user)

import os
import json
from datetime import datetime as dt


def get_json_data(file: str) -> dict:
    """Get all settings from json file"""
    if not os.path.exists(file):
        return dict()
    with open(file, 'r', encoding='utf-8') as file:
        quiz = json.load(file)
    return quiz


def save_user_data(file: str, name: str, quiz: str, score: list):
    """Save user data in json file"""
    data = get_json_data(file)
    for i in range(len(data)):
        if data[i]['name'] == name:
            date_now = dt.now().strftime('%d.%m.%Y %H:%M')
            if quiz in data[i]['results']:
                data[i]['results'][quiz].append([score[0], score[1], date_now])
            else:
                data[i]['results'][quiz] = [[score[0], score[1] , date_now]]
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
