from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from file_manager import (
    scan_folder,
    get_candidate_files,
    search_document_contents,
    read_file_content
)

from ai import (
    understand_command,
    rank_results,
    answer_file_question,
    generate_chat_response
)


app = FastAPI(
    title="MILO Backend"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FolderRequest(BaseModel):
    path: str


class CommandRequest(BaseModel):
    command: str
    folder: str
    chat_id: str = "default"


chat_memory = {}


def get_chat_memory(chat_id):
    if chat_id not in chat_memory:
        chat_memory[chat_id] = {
            "last_command": "",
            "last_action": "",
            "last_query": "",
            "last_file": None,
            "last_results": [],
            "last_file_content": "",
            "last_file_name": ""
        }

    return chat_memory[chat_id]


def add_conversation_message(
    memory,
    role,
    content
):
    if "_conversation" not in memory:
        memory["_conversation"] = []

    memory["_conversation"].append({
        "role": role,
        "content": content
    })

    if len(memory["_conversation"]) > 20:
        memory["_conversation"] = (
            memory["_conversation"][-20:]
        )


def get_conversation(memory):
    return memory.get(
        "_conversation",
        []
    )


@app.get("/")
def home():
    return {
        "message": "MILO backend is running."
    }


@app.post("/scan")
def scan(request: FolderRequest):
    try:
        files = scan_folder(
            request.path
        )

        return {
            "success": True,
            "folder": request.path,
            "files": files
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.post("/command")
def command(
    request: CommandRequest
):
    try:
        memory = get_chat_memory(
            request.chat_id
        )

        conversation = get_conversation(
            memory
        )

        previous_user_message = {
            "role": "user",
            "content": request.command
        }

        action = understand_command(
            request.command,
            conversation,
            memory
        )

        action_type = action.get(
            "action"
        )

        query = action.get(
            "query",
            request.command
        )

        memory["last_command"] = (
            request.command
        )

        memory["last_action"] = (
            action_type
        )

        memory["last_query"] = (
            query
        )

        add_conversation_message(
            memory,
            "user",
            request.command
        )

        conversation = get_conversation(
            memory
        )


        if action_type == "CHAT":

            answer = generate_chat_response(
                request.command,
                conversation,
                memory
            )

            add_conversation_message(
                memory,
                "assistant",
                answer
            )

            return {
                "success": True,
                "action": "CHAT",
                "query": query,
                "answer": answer
            }


        if action_type == "QUESTION":

            content_matches = (
                search_document_contents(
                    request.folder,
                    request.command,
                    limit=3
                )
            )

            if not content_matches:

                answer = (
                    "I couldn't find a file "
                    "containing the information "
                    "you're asking about."
                )

                add_conversation_message(
                    memory,
                    "assistant",
                    answer
                )

                return {
                    "success": True,
                    "action": "QUESTION",
                    "query": query,
                    "answer": answer
                }

            best_file = content_matches[0]

            content = read_file_content(
                best_file["path"]
            )

            if not content:

                answer = (
                    "I found the file, but "
                    "I couldn't read its contents."
                )

                add_conversation_message(
                    memory,
                    "assistant",
                    answer
                )

                return {
                    "success": True,
                    "action": "QUESTION",
                    "query": query,
                    "answer": answer
                }

            memory["last_file"] = {
                "name": best_file["name"],
                "path": best_file["path"]
            }

            memory["last_file_name"] = (
                best_file["name"]
            )

            memory["last_file_content"] = (
                content[:30000]
            )

            answer = answer_file_question(
                request.command,
                best_file["name"],
                content,
                conversation,
                memory
            )

            add_conversation_message(
                memory,
                "assistant",
                answer
            )

            return {
                "success": True,
                "action": "QUESTION",
                "query": query,
                "answer": answer,
                "file": {
                    "name": best_file["name"],
                    "path": best_file["path"]
                }
            }


        if action_type == "SEARCH":

            files = scan_folder(
                request.folder
            )

            candidates = get_candidate_files(
                files,
                request.command,
                limit=8
            )

            matches = []

            if candidates:

                matches = rank_results(
                    request.command,
                    candidates,
                    conversation,
                    memory
                )

            if matches:

                memory["last_results"] = matches

                memory["last_file"] = {
                    "name": matches[0]["name"],
                    "path": matches[0]["path"]
                }

                memory["last_file_name"] = (
                    matches[0]["name"]
                )

                return_message = (
                    f"I found "
                    f"{len(matches)} "
                    f"matching result"
                    f"{'s' if len(matches) != 1 else ''}."
                )

                memory["last_file_content"] = ""

                add_conversation_message(
                    memory,
                    "assistant",
                    return_message
                )

                return {
                    "success": True,
                    "action": "SEARCH",
                    "query": query,
                    "results": matches
                }

            content_matches = (
                search_document_contents(
                    request.folder,
                    request.command,
                    limit=5
                )
            )

            if content_matches:

                memory["last_results"] = (
                    content_matches
                )

                memory["last_file"] = {
                    "name": content_matches[0]["name"],
                    "path": content_matches[0]["path"]
                }

                memory["last_file_name"] = (
                    content_matches[0]["name"]
                )

                return_message = (
                    f"I found "
                    f"{len(content_matches)} "
                    f"matching result"
                    f"{'s' if len(content_matches) != 1 else ''}."
                )

                memory["last_file_content"] = ""

                add_conversation_message(
                    memory,
                    "assistant",
                    return_message
                )

                return {
                    "success": True,
                    "action": "SEARCH",
                    "query": query,
                    "results": content_matches
                }

            answer = (
                "I couldn't find anything "
                "matching that."
            )

            add_conversation_message(
                memory,
                "assistant",
                answer
            )

            return {
                "success": True,
                "action": "SEARCH",
                "query": query,
                "results": []
            }


        answer = (
            "I'm not sure what you want me "
            "to do yet."
        )

        add_conversation_message(
            memory,
            "assistant",
            answer
        )

        return {
            "success": True,
            "action": "CHAT",
            "answer": answer
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )