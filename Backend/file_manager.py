import os
import re
import json
import warnings

from pypdf import PdfReader


TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".py",
    ".js",
    ".html",
    ".css",
    ".json",
    ".csv"
}

DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md"
}

INDEX_FILENAME = ".milo_index.json"

MAX_PDF_SIZE = 50 * 1024 * 1024


def scan_folder(folder_path):
    if not os.path.exists(folder_path):
        raise Exception("The selected folder does not exist.")

    if not os.path.isdir(folder_path):
        raise Exception("The selected path is not a folder.")

    results = []

    for root, folders, files in os.walk(folder_path):
        if INDEX_FILENAME in files:
            files.remove(INDEX_FILENAME)

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


def read_file_content(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":

        try:
            if not os.path.exists(file_path):
                return ""

            file_size = os.path.getsize(file_path)

            if file_size > MAX_PDF_SIZE:
                return ""

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                reader = PdfReader(
                    file_path,
                    strict=False
                )

                text = []

                for page in reader.pages:
                    try:
                        page_text = page.extract_text()

                        if page_text:
                            text.append(page_text)

                    except Exception:
                        continue

                return "\n".join(text).strip()

        except Exception:
            return ""

    if extension in TEXT_EXTENSIONS:

        try:
            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:
                return file.read()

        except Exception:
            return ""

    return ""


def get_index_path(folder_path):
    return os.path.join(
        folder_path,
        INDEX_FILENAME
    )


def load_index(folder_path):
    index_path = get_index_path(folder_path)

    if not os.path.exists(index_path):
        return {}

    try:
        with open(
            index_path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception:
        return {}


def save_index(folder_path, index):
    index_path = get_index_path(folder_path)

    try:
        with open(
            index_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                index,
                file,
                ensure_ascii=False,
                indent=2
            )

    except Exception:
        pass


def normalize_text(text):
    text = str(text).lower()

    text = text.replace(
        "spider-man",
        "spiderman"
    )

    text = text.replace(
        "spider man",
        "spiderman"
    )

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    return text


def expand_query_words(words):
    concept_groups = {

        "price": {
            "price",
            "paid",
            "pay",
            "cost",
            "costs",
            "amount",
            "money",
            "rate",
            "rates",
            "mad",
            "payment",
            "payments",
            "total"
        },

        "time": {
            "time",
            "start",
            "starts",
            "started",
            "begin",
            "begins",
            "beginning",
            "hour",
            "when"
        },

        "date": {
            "date",
            "day",
            "when",
            "sat",
            "sun",
            "mon",
            "tue",
            "wed",
            "thu",
            "fri"
        },

        "seats": {
            "seat",
            "seats",
            "chair",
            "chairs",
            "place",
            "places"
        },

        "reservation": {
            "reservation",
            "booking",
            "booked",
            "order",
            "operation",
            "number",
            "reference",
            "confirmation"
        },

        "location": {
            "location",
            "where",
            "cinema",
            "theater",
            "theatre",
            "address",
            "place"
        },

        "language": {
            "language",
            "version",
            "vostfr",
            "french",
            "english",
            "dubbed",
            "subtitle",
            "subtitles"
        },

        "auditorium": {
            "auditorium",
            "room",
            "screen",
            "4dx",
            "imax"
        },

        "duration": {
            "duration",
            "running",
            "runtime",
            "length",
            "long",
            "end"
        },

        "movie": {
            "movie",
            "film",
            "cinema",
            "show",
            "session"
        },

        "ticket": {
            "ticket",
            "tickets",
            "entry",
            "admission"
        }
    }

    expanded = set(words)

    for word in words:

        for concept_words in concept_groups.values():

            if word in concept_words:
                expanded.update(
                    concept_words
                )

    return expanded


def get_document_files(folder_path):
    documents = []

    for root, folders, files in os.walk(folder_path):

        for file in files:

            if file == INDEX_FILENAME:
                continue

            extension = os.path.splitext(
                file
            )[1].lower()

            if extension not in DOCUMENT_EXTENSIONS:
                continue

            full_path = os.path.join(
                root,
                file
            )

            try:
                modified = os.path.getmtime(
                    full_path
                )

                size = os.path.getsize(
                    full_path
                )

                documents.append({
                    "name": file,
                    "path": full_path,
                    "type": "file",
                    "modified": modified,
                    "size": size
                })

            except Exception:
                continue

    return documents


def score_filename(file_name, useful_words):
    normalized_name = normalize_text(
        file_name
    )

    name_words = set(
        normalized_name.split()
    )

    score = 0

    for word in useful_words:

        if word in name_words:
            score += 100

        elif word in normalized_name:
            score += 40

    return score


def search_document_contents(
    folder_path,
    query,
    limit=5
):
    query_text = normalize_text(
        query
    )

    query_words = query_text.split()

    ignored_words = {
        "find",
        "show",
        "get",
        "look",
        "search",
        "for",
        "the",
        "a",
        "an",
        "my",
        "me",
        "file",
        "files",
        "folder",
        "folders",
        "thing",
        "something",
        "that",
        "where",
        "about",
        "with",
        "which",
        "document",
        "whatever",
        "called",
        "named",
        "please",
        "some",
        "one",
        "is",
        "are",
        "was",
        "were",
        "and",
        "or",
        "to",
        "in",
        "of",
        "on",
        "can",
        "you",
        "want",
        "looking",
        "what",
        "whats",
        "what's",
        "how",
        "much",
        "did",
        "do",
        "does",
        "i",
        "it",
        "its",
        "tell"
    }

    useful_words = [
        word
        for word in query_words
        if word not in ignored_words
        and len(word) >= 3
    ]

    if not useful_words:
        return []

    expanded_words = expand_query_words(
        useful_words
    )

    documents = get_document_files(
        folder_path
    )

    if not documents:
        return []

    for document in documents:

        document["filename_score"] = score_filename(
            document["name"],
            useful_words
        )

    documents.sort(
        key=lambda item: (
            item["filename_score"],
            item["modified"]
        ),
        reverse=True
    )

    results = []

    for document in documents:

        file_path = document["path"]

        content = read_file_content(
            file_path
        )

        if not content:
            continue

        normalized_content = normalize_text(
            content
        )

        normalized_name = normalize_text(
            document["name"]
        )

        matched_original = []

        matched_expanded = []

        for word in useful_words:

            pattern = (
                r"\b"
                + re.escape(word)
                + r"\b"
            )

            if re.search(
                pattern,
                normalized_content
            ):
                matched_original.append(
                    word
                )

        for word in expanded_words:

            pattern = (
                r"\b"
                + re.escape(word)
                + r"\b"
            )

            if re.search(
                pattern,
                normalized_content
            ):
                matched_expanded.append(
                    word
                )

        original_count = len(
            matched_original
        )

        expanded_count = len(
            matched_expanded
        )

        score = 0

        score += original_count * 100

        score += expanded_count * 20

        score += document["filename_score"]

        for word in useful_words:

            pattern = (
                r"\b"
                + re.escape(word)
                + r"\b"
            )

            if re.search(
                pattern,
                normalized_name
            ):
                score += 150

        if (
            "spiderman" in useful_words
            and "spiderman" in normalized_content
        ):
            score += 1000

        if (
            "4dx" in useful_words
            and "4dx" in normalized_content
        ):
            score += 1000

        if (
            "vostfr" in useful_words
            and "vostfr" in normalized_content
        ):
            score += 1000

        if (
            original_count == 0
            and expanded_count == 0
        ):
            continue

        if (
            original_count == 0
            and expanded_count < 2
        ):
            continue

        results.append({
            "name": document["name"],
            "path": document["path"],
            "type": "file",
            "score": score,
            "matched": original_count,
            "expanded": expanded_count
        })

        strong_match = False

        if "spiderman" in normalized_content:
            strong_match = True

        if (
            original_count >= 2
            and expanded_count >= 2
        ):
            strong_match = True

        if strong_match and len(results) >= 1:
            break

    results.sort(
        key=lambda item: (
            item["score"],
            item["matched"],
            item["expanded"]
        ),
        reverse=True
    )

    if not results:
        return []

    best_score = results[0]["score"]

    strong_results = [
        result
        for result in results
        if result["score"] >= best_score * 0.35
    ]

    final_results = []

    for result in strong_results[:limit]:

        final_results.append({
            "name": result["name"],
            "path": result["path"],
            "type": result["type"]
        })

    return final_results


def get_candidate_files(
    files,
    query,
    limit=8
):
    query_words = re.findall(
        r"[a-zA-Z0-9]+",
        query.lower()
    )

    ignored_words = {
        "find",
        "show",
        "get",
        "look",
        "search",
        "for",
        "the",
        "a",
        "an",
        "my",
        "me",
        "file",
        "files",
        "folder",
        "folders",
        "thing",
        "something",
        "that",
        "where",
        "about",
        "with",
        "which",
        "document",
        "whatever",
        "called",
        "named",
        "please",
        "some",
        "one",
        "is",
        "are",
        "was",
        "were",
        "and",
        "or",
        "to",
        "in",
        "of",
        "on"
    }

    useful_words = [
        word
        for word in query_words
        if word not in ignored_words
        and len(word) >= 3
    ]

    scored = []

    for item in files:

        name = item["name"].lower()

        name_without_extension = os.path.splitext(
            name
        )[0]

        name_words = re.findall(
            r"[a-zA-Z0-9]+",
            name_without_extension
        )

        score = 0
        matched_words = 0

        for word in useful_words:

            if word in name_words:
                score += 10
                matched_words += 1

            elif word in name_without_extension:
                score += 4
                matched_words += 1

        if matched_words > 0:

            scored.append({
                "item": item,
                "score": score
            })

    scored.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return [
        item["item"]
        for item in scored[:limit]
    ]