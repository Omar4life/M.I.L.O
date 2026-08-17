from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from file_manager import scan_folder, search_files
from ai import understand_command

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
        action = understand_command(request.command)

        if action.get("action") == "SEARCH":
            query = action.get("query", "")
            files = scan_folder(request.folder)
            matches = search_files(files, query)

            return {
                "success": True,
                "action": "SEARCH",
                "query": query,
                "results": matches
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