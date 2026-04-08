# Store/change/get json data (quiz, user)

import os
import json
from datetime import datetime as dt


def get_json_data(file: str) -> list:
    """Get data from json file"""
    if not os.path.exists(file):
        return list()
    with open(file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


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


def save_data(file: str, data: list):
    """Save data in json file"""
    if not os.path.exists(file):
        raise FileNotFoundError(f'File "{file}" not found')
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
