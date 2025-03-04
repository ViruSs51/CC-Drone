import json


def open_json(filename: str) -> dict:
    with open(filename, "r", encoding="utf-8") as file:
        content = json.loads(file.read())

        return content


def write_json(filename: str, content):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(content, indent=4))
