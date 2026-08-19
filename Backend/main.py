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
    answer_file_question
)

app = FastAPI(title="MILO Backend")

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


@app.get("/")
def home():
    return {
        "message": "MILO backend is running."
    }


@app.post("/scan")
def scan(request: FolderRequest):
    try:
        files = scan_folder(request.path)

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
def command(request: CommandRequest):
    try:
        action = understand_command(
            request.command
        )

        action_type = action.get(
            "action"
        )

        query = action.get(
            "query",
            request.command
        )

        if action_type == "QUESTION":

            content_matches = search_document_contents(
                request.folder,
                request.command,
                limit=3
            )

            if not content_matches:
                return {
                    "success": True,
                    "action": "QUESTION",
                    "query": query,
                    "answer": "I couldn't find a file containing the information you're asking about."
                }

            best_file = content_matches[0]

            content = read_file_content(
                best_file["path"]
            )

            if not content:
                return {
                    "success": True,
                    "action": "QUESTION",
                    "query": query,
                    "answer": "I found the file, but I couldn't read its contents."
                }

            answer = answer_file_question(
                request.command,
                best_file["name"],
                content
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
                    candidates
                )

            if matches:
                return {
                    "success": True,
                    "action": "SEARCH",
                    "query": query,
                    "results": matches
                }

            content_matches = search_document_contents(
                request.folder,
                request.command,
                limit=5
            )

            return {
                "success": True,
                "action": "SEARCH",
                "query": query,
                "results": content_matches
            }

        return {
            "success": False,
            "message": "MILO does not support that action yet."
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )