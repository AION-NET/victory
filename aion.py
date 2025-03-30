#   AION.py
#   RWX (c) 2025 Gregory L. Magnusson BANKON
#   Secure API for file and command execution with GPT-4 agent interaction
import os
import shutil
import subprocess
import logging
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status, Query, Body
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, validator
from config import BASE_DIRECTORY, API_TOKEN
from urllib.parse import unquote
import shlex
from dotenv import load_dotenv

app = FastAPI(title="AION RWX API")

#   --- Load Environment Variables ---
load_dotenv()  #   Load variables from .env file

#   --- Logging Setup ---
LOG_DIR = os.path.join(BASE_DIRECTORY, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "activity.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

#   --- Security ---
def verify_api_token(request: Request):
    """
    Verifies the API token in the request headers.

    Args:
        request: The incoming request.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid or missing.
    """
    token = request.headers.get("action-api-key")
    if not token or token != API_TOKEN:
        logging.warning("Unauthorized access attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

#   --- Path Handling ---
def safe_path(sub_path: str) -> str:
    """
    Constructs a safe absolute path, preventing access outside the BASE_DIRECTORY.
    Decodes URL-encoded paths.  Handles various edge cases.

    Args:
        sub_path: The sub-path to append to BASE_DIRECTORY.

    Returns:
        The safe absolute path.

    Raises:
        HTTPException: 403 Forbidden if the path is unsafe.
        HTTPException: 400 Bad Request if the path is invalid.
    """
    if not sub_path:
        return BASE_DIRECTORY
    try:
        decoded_path = unquote(sub_path)  #   Decode URL-encoded paths
        normalized_path = os.path.normpath(decoded_path)
        full_path = os.path.abspath(os.path.join(BASE_DIRECTORY, normalized_path))
        if not full_path.startswith(os.path.abspath(BASE_DIRECTORY)):
            logging.warning(f"Unsafe path access attempted: {full_path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
            )
        return full_path
    except ValueError as ve:
        logging.error(f"Invalid path: {sub_path} - {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid path: {ve}"
        )
    except Exception as e:
        logging.error(f"Error processing path: {sub_path} - {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path"
        )

#   --- Command Whitelisting ---
def load_whitelist() -> List[str]:
    """
    Loads the command whitelist from 'whitelist.json'.

    Returns:
        A list of allowed commands.
        Returns an empty list and logs an error if the file is not found or invalid.
    """
    try:
        with open("whitelist.json", "r") as file:
            whitelist_data = json.load(file)
        return whitelist_data.get("allowed_commands", [])
    except FileNotFoundError:
        logging.error("whitelist.json not found. API might be unstable.")
        return []  #   Return an empty list to avoid errors
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in whitelist.json.")
        return []

ALLOWED_COMMANDS = load_whitelist()

def is_command_allowed(command: str) -> bool:
    """
    Enhanced command whitelisting with better matching.
    Allows exact matches and command prefix matching with limited safe arguments.
    Also allows execution of scripts (.sh, .py, etc.) under specific conditions.

    Args:
        command: The command to check.
        whitelist: The list of allowed commands.

    Returns:
        True if the command is allowed, False otherwise.
    """
    normalized_command = command.strip().lower()
    parts = shlex.split(normalized_command)  #   Safely split the command

    for allowed in ALLOWED_COMMANDS:
        normalized_allowed = allowed.strip().lower()
        allowed_parts = shlex.split(normalized_allowed)

        if parts == allowed_parts:  #   Exact match
            return True

        #   Match command prefixes with limited safe arguments
        if len(parts) > len(allowed_parts) and parts[:len(allowed_parts)] == allowed_parts:
            #   Basic check for potentially dangerous arguments (can be expanded)
            safe_args_pattern = re.compile(r'^[a-z0-9\-_./]+$')  #   Allow only basic args
            if all(safe_args_pattern.match(arg) for arg in parts[len(allowed_parts):]):
                return True

    #   Script execution (more restrictive)
    if parts[0] in ("python3", "python") and parts[-1].endswith((".sh", ".py", ".pl", ".rb", ".bash")):
        script_path = parts[-1]
        if safe_path(BASE_DIRECTORY, script_path) == os.path.abspath(script_path):  #   Very strict path check
            return True

    return False

#   --- API Endpoints ---
@app.get("/list/")
async def list_files(
    request: Request,
    path: Optional[str] = Query(None, description="Path to list (optional)"),
):
    """
    Lists files and directories in a specified path.

    Args:
        request: The incoming request.
        path: The path to list. If None, lists the base directory.

    Returns:
        A JSON response containing a list of files.

    Raises:
        HTTPException: 404 Not Found if the folder does not exist.
        HTTPException: 500 Internal Server Error if an error occurs during file listing.
    """
    verify_api_token(request)
    target_path = safe_path(path)
    if not os.path.exists(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )
    try:
        files = os.listdir(target_path)
        return JSONResponse({"files": files})
    except OSError as e:
        logging.error(f"Error listing files in {target_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {e}",
        )

class ReadFileResponse(BaseModel):
    content: str
    #   Response model for /read/ endpoint

@app.get("/read/")
async def read_file(
    request: Request,
    file_path: str = Query(..., description="Path to the file to read"),
):
    """
    Reads the content of a specified file.

    Args:
        request: The incoming request.
        file_path: The path to the file to read.

    Returns:
        A JSON response containing the file's content.

    Raises:
        HTTPException: 404 Not Found if the file does not exist.
        HTTPException: 500 Internal Server Error if an error occurs while reading the file.
    """
    verify_api_token(request)
    target_path = safe_path(file_path)
    if not os.path.isfile(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    try:
        with open(target_path, "r") as file:
            content = file.read()
        return JSONResponse({"content": content})
    except OSError as e:
        logging.error(f"Error reading file {target_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {e}",
        )

class ExecuteCommandRequest(BaseModel):
    command: str
    #   Request model for /execute/ endpoint

    @validator("command")
    def sanitize_command(cls, value: str):
        """
        Basic command sanitization (can be expanded).
        Currently just strips whitespace.  Further sanitization should be added.
        """
        return value.strip()

class ExecuteCommandResponse(BaseModel):
    status: str
    output: str
    #   Response model for /execute/ endpoint

@app.post("/execute/")
async def execute_command(
    request: Request, command_request: ExecuteCommandRequest,
):
    """
    Executes a whitelisted shell command.

    Args:
        request: The incoming request.
        command_request: The request body containing the command to execute.

    Returns:
        A JSON response with the command's output or an error message.

    Raises:
        HTTPException: 400 Bad Request if the command is empty or fails.
        HTTPException: 403 Forbidden if the command is not allowed.
        HTTPException: 500 Internal Server Error for unexpected errors.
    """
    verify_api_token(request)
    command = command_request.command
    if not command:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Command cannot be empty"
        )
    if not is_command_allowed(command):
        logging.warning(f"Unauthorized command attempt: {command}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Command not allowed"
        )
    try:
        logging.info(f"Executing command: {command}")
        process = subprocess.Popen(
            shlex.split(command),  #   Use shlex.split for safety
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output, error = process.communicate(timeout=15)  #   Timeout to prevent hangs
        if process.returncode != 0:
            logging.error(f"Command failed: {command} | Error: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=output or error or "Command failed"
            )
        logging.info(f"Command output: {output}")
        return JSONResponse({"status": "success", "output": output})
    except subprocess.TimeoutExpired:
        process.kill()
        logging.error(f"Command timed out: {command}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Command timed out"
        )
    except OSError as e:
        logging.error(f"OS Error executing command: {command} | {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OS error: {e}"
        )
    except Exception as e:
        logging.error(f"Unexpected error executing command: {command} | {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )

#   --- File Management ---
class FileOperationResponse(BaseModel):
    status: str
    message: str
    #   Response model for file operations

@app.post("/create_file/")
async def create_file(
    request: Request,
    file_path: str = Query(..., description="Path for the new file"),
    content: str = Body("", description="Initial file content (optional)"),
):
    """
    Creates a new file with optional content.

    Args:
        request: The incoming request.
        file_path: The path for the new file.
        content: The initial content of the file (optional).

    Returns:
        A JSON response indicating the success or failure of the operation.

    Raises:
        HTTPException: 409 Conflict if the file already exists.
        HTTPException: 500 Internal Server Error if an error occurs during file creation.
    """
    verify_api_token(request)
    target_path = safe_path(file_path)
    if os.path.exists(target_path):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="File already exists"
        )
    try:
        with open(target_path, "w") as file:
            file.write(content)
        logging.info(f"File created: {target_path}")
        return JSONResponse({"status": "success", "message": "File created"})
    except OSError as e:
        logging.error(f"Error creating file {target_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create file: {e}",
        )

@app.delete("/delete_file/")
async def delete_file(
    request: Request, file_path: str = Query(..., description="Path to the file to delete"),
):
    """
    Deletes a specified file.

    Args:
        request: The incoming request.
        file_path: The path to the file to delete.

    Returns:
        A JSON response indicating the success or failure of the operation.

    Raises:
        HTTPException: 404 Not Found if the file does not exist.
        HTTPException: 500 Internal Server Error if an error occurs during file deletion.
    """
    verify_api_token(request)
    target_path = safe_path(file_path)
    if not os.path.exists(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    try:
        os.remove(target_path)
        logging.info(f"File deleted: {target_path}")
        return JSONResponse({"status": "success", "message": "File deleted"})
    except OSError as e:
        logging.error(f"Error deleting file {target_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {e}",
        )

@app.put("/rename_file/")
async def rename_file(
    request: Request,
    old_file_path: str = Query(..., description="Current path of the file"),
    new_file_path: str = Query(..., description="New path for the file"),
):
    """
    Renames a file.

    Args:
        request: The incoming request.
        old_file_path: The current path of the file.
        new_file_path: The new path for the file.

    Returns:
        A JSON response indicating the success or failure of the operation.

    Raises:
        HTTPException: 404 Not Found if the file does not exist.
        HTTPException: 409 Conflict if a file already exists at the new path.
        HTTPException: 500 Internal Server Error if an error occurs during renaming.
    """
    verify_api_token(request)
    old_path = safe_path(old_file_path)
    new_path = safe_path(new_file_path)
    if not os.path.exists(old_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    if os.path.exists(new_path):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="File already exists at new path"
        )
    try:
        os.rename(old_path, new_path)
        logging.info(f"File renamed from {old_path} to {new_path}")
        return JSONResponse({"status": "success", "message": "File renamed"})
    except OSError as e:
        logging.error(f"Error renaming file from {old_path} to {new_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rename file: {e}",
        )

#   --- Directory Management ---
@app.post("/create_directory/")
async def create_directory(
    request: Request, dir_path: str = Query(..., description="Path for the new directory"),
    recursive: bool = Query(False, description="Create parent directories if they don't exist")
):
    """
    Creates a new directory.

    Args:
        request: The incoming request.
        dir_path: The path for the new directory.
        recursive: If True, creates parent directories as needed.

    Returns:
        A JSON response indicating the success or failure of the operation.

    Raises:
        HTTPException: 409 Conflict if the directory already exists (and recursive is False).
        HTTPException: 500 Internal Server Error if an error occurs during directory creation.
    """
    verify_api_token(request)
    target_path = safe_path(dir_path)
    try:
        if recursive:
            os.makedirs(target_path, exist_ok=True)  #   Create directories recursively
        else:
            os.makedirs(target_path)
        logging.info(f"Directory created: {target_path} (recursive={recursive})")
        return JSONResponse({"status": "success", "message": "Directory created"})
    except FileExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Directory already exists"
        )
    except OSError as e:
        logging.error(f"Error creating directory {target_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create directory: {e}",
        )

@app.delete("/delete_directory/")
async def delete_directory(
    request: Request,
    dir_path: str = Query(..., description="Path to the directory to delete"),
    recursive: bool = Query(False, description="Delete directory and its contents"),
):
    """
    Deletes a specified directory.

    Args:
        request: The incoming request.
        dir_path: The path to the directory to delete.
        recursive: If True, deletes the directory and its contents (rmtree).

    Returns:
        A JSON response indicating the success or failure of the operation.

    Raises:
        HTTPException: 404 Not Found if the directory does not exist.
        HTTPException: 500 Internal Server Error if an error occurs during directory deletion.
    """
    verify_api_token(request)
    target_path = safe_path(dir_path)
    if not os.path.exists(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found"
        )
    try:
        if recursive:
            shutil.rmtree(target_path)
            logging.info(f"Directory deleted recursively: {target_path}")
        else:
            os.rmdir(target_path)
            logging.info(f"Directory deleted: {target_path}")
        return JSONResponse({"status": "success", "message": "Directory deleted"})
    except OSError as e:
        logging.error(f"Error deleting directory {target_path} (recursive={recursive}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete directory: {e}",
        )
