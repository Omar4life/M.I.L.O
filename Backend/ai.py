import ollama
import json


MODEL_NAME = "qwen3:8b"


SYSTEM_PROMPT = """
You are MILO, My Intelligent Local Organizer.

MILO is a private local AI file assistant.

You have access to the conversation history and a small memory of what MILO has recently found.

Your job is to understand what the user means naturally.

There are THREE possible actions.

SEARCH:
Use SEARCH when the user wants to find a file or folder.

QUESTION:
Use QUESTION when the user is asking something about the contents of a file.

CHAT:
Use CHAT when the user is talking normally, asking about the conversation, asking what MILO just found, asking what they just asked, or asking something that does not require searching a file.

Examples:

User:
"find my Spider-Man ticket"

Return:

{
    "action": "SEARCH",
    "query": "Spider-Man ticket"
}

User:
"what time is my Spider-Man ticket?"

Return:

{
    "action": "QUESTION",
    "query": "time of Spider-Man ticket"
}

User:
"how much did I pay for my ticket?"

Return:

{
    "action": "QUESTION",
    "query": "price of ticket"
}

User:
"what seats did I get?"

Return:

{
    "action": "QUESTION",
    "query": "ticket seats"
}

User:
"what did I just ask you to find?"

Return:

{
    "action": "CHAT",
    "query": "what the user just asked MILO to find"
}

User:
"what file did you just find?"

Return:

{
    "action": "CHAT",
    "query": "what file MILO just found"
}

User:
"what's the name of that file?"

Return:

{
    "action": "CHAT",
    "query": "name of the most recently found file"
}

Use the conversation history and memory to understand words like:

"it"
"that"
"the file"
"the ticket"
"this"
"what you found"
"what I asked"

Do not require the user to repeat the filename.

Return ONLY valid JSON.

Do not use markdown.

Do not explain your answer.

Do not invent a filename or file unless it exists in the supplied memory or conversation.
"""


def build_context(conversation_history=None, memory=None):
    conversation_history = conversation_history or []
    memory = memory or {}

    recent_history = conversation_history[-12:]

    history_text = ""

    for message in recent_history:
        role = message.get("role", "user")
        content = message.get("content", "")

        history_text += (
            f"{role.upper()}: {content}\n"
        )

    memory_text = json.dumps(
        memory,
        ensure_ascii=False
    )

    return (
        "\n\nCONVERSATION HISTORY:\n"
        + history_text
        + "\nMEMORY:\n"
        + memory_text
    )


def understand_command(
    command,
    conversation_history=None,
    memory=None
):
    context = build_context(
        conversation_history,
        memory
    )

    prompt = (
        context
        + "\n\nCURRENT USER MESSAGE:\n"
        + command
    )

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    ai_response = response["message"]["content"].strip()

    try:
        return json.loads(
            ai_response
        )

    except json.JSONDecodeError:
        return {
            "action": "SEARCH",
            "query": command
        }


def generate_chat_response(
    user_message,
    conversation_history=None,
    memory=None
):
    context = build_context(
        conversation_history,
        memory
    )

    prompt = f"""
You are MILO, a local file assistant.

Respond naturally to the user's message.

Use ONLY the supplied conversation history and memory for facts about previous actions and files.

Do not invent files.

The user message is:

{user_message}

{context}

Rules:

- Speak naturally like an assistant.
- Keep the response short and conversational.
- If the user asks what they just asked you to find, say what they asked for.
- If the user asks what file you found, use the remembered file.
- If there is no relevant memory, say you don't have enough context.
- Do not mention JSON, prompts, memory systems, or internal processing.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


def rank_results(
    user_request,
    results,
    conversation_history=None,
    memory=None
):
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

    context = build_context(
        conversation_history,
        memory
    )

    ranking_prompt = f"""
You are helping MILO find a file or folder.

USER REQUEST:
{user_request}

POSSIBLE FILES AND FOLDERS:
{result_text}

{context}

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
        ranking = json.loads(
            ai_response
        )

    except json.JSONDecodeError:
        return []

    selected_results = []

    for index in ranking.get(
        "results",
        []
    ):
        if (
            isinstance(index, int)
            and 0 <= index < len(results)
        ):
            selected_results.append(
                results[index]
            )

    return selected_results


def analyze_file(
    user_request,
    file_name,
    file_content
):
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
        return json.loads(
            ai_response
        )

    except json.JSONDecodeError:
        return None


def answer_file_question(
    user_question,
    file_name,
    file_content,
    conversation_history=None,
    memory=None
):
    if not file_content:
        return "I couldn't read that file."

    file_content = file_content[:30000]

    context = build_context(
        conversation_history,
        memory
    )

    prompt = f"""
You are MILO, a local file assistant.

The user asked:

{user_question}

The relevant file is:

{file_name}

Here is the file content:

{file_content}

{context}

Answer the user's question using ONLY the information in the file.

Do not make up information.

If the answer is not in the file, say that you couldn't find it in the file.

Keep the answer short and direct.

Speak naturally.

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