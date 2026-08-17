import os
import re

def scan_folder(folder_path):
    if not os.path.exists(folder_path):
        raise Exception("The selected folder does not exist.")

    if not os.path.isdir(folder_path):
        raise Exception("The selected path is not a folder.")

    results = []

    for root, folders, files in os.walk(folder_path):
        for folder in folders:
            full_path = os.path.join(root, folder)
            results.append({
                "name": folder,
                "path": full_path,
                "type": "folder"
            })

        for file in files:
            full_path = os.path.join(root, file)
            results.append({
                "name": file,
                "path": full_path,
                "type": "file"
            })

    return results

def search_files(files, query):
    query = query.lower()
    query = query.replace("$", " ")
    query_words = re.findall(r"[a-zA-Z0-9]+", query)

    ignored_words = {
        "the",
        "a",
        "an",
        "my",
        "me",
        "i",
        "find",
        "show",
        "get",
        "look",
        "for",
        "where",
        "can",
        "could",
        "would",
        "is",
        "are",
        "was",
        "were",
        "in",
        "on",
        "at",
        "to",
        "of",
        "and",
        "or",
        "with",
        "under",
        "less",
        "than"
    }

    useful_words = [
        word
        for word in query_words
        if word not in ignored_words
    ]

    matches = []

    for item in files:
        name = item["name"].lower()
        normalized_name = name.replace("$", " ")
        name_words = re.findall(r"[a-zA-Z0-9]+", normalized_name)
        score = 0

        for word in useful_words:
            if word in name_words:
                score += 1
            elif any(word in name_word for name_word in name_words):
                score += 0.5

        if score > 0:
            result = {
                "name": item["name"],
                "path": item["path"],
                "type": item["type"],
                "score": score
            }

            matches.append(result)

    matches.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    for item in matches:
        del item["score"]

    return matches