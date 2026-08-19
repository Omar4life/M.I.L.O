import ollama
import json

MODEL_NAME = "qwen3:8b"

SYSTEM_PROMPT = """
You are MILO, My Intelligent Local Organizer.

MILO is an AI-powered local file manager.

Understand what the user wants.

There are two possible actions.

SEARCH:
Use SEARCH when the user wants to find a file or folder.

QUESTION:
Use QUESTION when the user is asking something about the contents of a file.

Return ONLY valid JSON.

For SEARCH use:

{
    "action": "SEARCH",
    "query": "short description of what the user wants"
}

For QUESTION use:

{
    "action": "QUESTION",
    "query": "short description of the information the user wants"
}

Examples:

"find my Spider-Man ticket"

{
    "action": "SEARCH",
    "query": "Spider-Man ticket"
}

"what time is my Spider-Man ticket?"

{
    "action": "QUESTION",
    "query": "time of Spider-Man ticket"
}

"how much did I pay for my ticket?"

{
    "action": "QUESTION",
    "query": "price of ticket"
}

"what seats did I get?"

{
    "action": "QUESTION",
    "query": "ticket seats"
}

Do not include markdown.

Do not explain your answer.
"""


def understand_command(command):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": command
            }
        ]
    )

    ai_response = response["message"]["content"].strip()

    try:
        return json.loads(ai_response)

    except json.JSONDecodeError:
        return {
            "action": "SEARCH",
            "query": command
        }


def rank_results(user_request, results):
    if not results:
        return []

    result_text = ""

    for index, item in enumerate(results):
        result_text += (
            f"{index}: "
            f"{item['type']} | "
            f"{item['name']} | "
            f"{item['path']}\n"
        )

    ranking_prompt = f"""
You are helping MILO find a file or folder.

USER REQUEST:
{user_request}

POSSIBLE FILES AND FOLDERS:
{result_text}

Choose ONLY genuinely relevant results.

Think about the meaning of the request.

Do not select a result just because it contains one generic word.

Return ONLY valid JSON.

Use:

{{
    "results": [0, 1]
}}

Return a maximum of 3 results.

If nothing is genuinely relevant:

{{
    "results": []
}}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": ranking_prompt
            }
        ]
    )

    ai_response = response["message"]["content"].strip()

    try:
        ranking = json.loads(ai_response)

    except json.JSONDecodeError:
        return []

    selected_results = []

    for index in ranking.get("results", []):
        if isinstance(index, int) and 0 <= index < len(results):
            selected_results.append(results[index])

    return selected_results


def analyze_file(user_request, file_name, file_content):
    if not file_content:
        return None

    file_content = file_content[:20000]

    prompt = f"""
You are MILO.

The user wants to find:

{user_request}

You are checking:

{file_name}

FILE CONTENT:
{file_content}

Does the CONTENT actually match what the user is looking for?

Ignore the filename.

Read the actual content.

Return ONLY JSON:

{{
    "relevant": true,
    "reason": "short explanation"
}}

or:

{{
    "relevant": false,
    "reason": ""
}}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    ai_response = response["message"]["content"].strip()

    try:
        return json.loads(ai_response)

    except json.JSONDecodeError:
        return None


def answer_file_question(
    user_question,
    file_name,
    file_content
):
    if not file_content:
        return "I couldn't read that file."

    file_content = file_content[:30000]

    prompt = f"""
You are MILO, a local file assistant.

The user asked:

{user_question}

The relevant file is:

{file_name}

Here is the file content:

{file_content}

Answer the user's question using ONLY the information in the file.

Do not make up information.

If the answer is not in the file, say that you couldn't find it in the file.

Keep the answer short and direct.

Do not mention that you are an AI.

Do not explain your reasoning.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()