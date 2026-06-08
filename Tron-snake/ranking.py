# ranking.py
import json
RANK_FILE = "local_rank.json"

def add_rank(name, score):
    """Добавить очки в локальный рейтинг"""
    try:
        with open(RANK_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append({"name": name, "score": score})
    data = sorted(data, key=lambda x: x["score"], reverse=True)[:10]

    with open(RANK_FILE, "w") as f:
        json.dump(data, f)
    return data

def load_rank():
    """Загрузить локальный рейтинг"""
    try:
        with open(RANK_FILE, "r") as f:
            return json.load(f)
    except:
        return []