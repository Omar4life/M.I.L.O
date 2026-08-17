import ollama

import json


MODEL_NAME = "qwen3:8b"


SYSTEM_PROMPT = """
You are MILO, My Intelligent Local Organizer.

MILO is an AI-powered file manager.

Your job is to understand what the user wants to find in their files.

For now, MILO ONLY supports searching for files and folders.

The user might say:

"find my robotics files"
"show me my school files"
"find my resume"
"look for my math homework"
"find PDFs"

You must return ONLY valid JSON.

Use this exact structure:

{
    "action": "SEARCH",
    "query": "search term"
}

IMPORTANT RULES:

1. The query MUST be short.
2. The query MUST contain only the most important search words.
3. NEVER return multiple alternative search terms.
4. NEVER return synonyms.
5. NEVER return explanations.
6. NEVER use commas.
7. NEVER use the words "file", "files", "folder", or "folders" unless the user is specifically searching for one of those words.
8. For "find my robotics files", return "robotics".
9. For "find my math homework", return "math homework".
10. For "find my resume", return "resume".

Return ONLY JSON.
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

    ai_response = response["message"]["content"]

    ai_response = ai_response.strip()

    try:
        result = json.loads(ai_response)

    except json.JSONDecodeError:
        raise Exception("MILO's AI returned an invalid command.")

    return result