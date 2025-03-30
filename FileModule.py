#   FileModule.py
#   File-related operations for the AION RWX API

import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Query, Body, Request
from fastapi.responses import FileResponse, JSONResponse
from SecurityModule import safe_path, verify_api_token  #   Import security functions
from pydantic import BaseModel

#   (FastAPI app instance is expected to be initialized elsewhere and passed in)

def setup_file_endpoints(app: FastAPI, base_dir: str):
    """
    Sets up file-related API endpoints (create, read, delete, rename).

    Args:
        app: The FastAPI application instance.
        base_dir: The base directory for file operations.
    """

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
        """
        verify_api_token(request)
        target_path = safe_path(base_dir, file_path)
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
        """
        verify_api_token(request)
        target_path = safe_path(base_dir, file_path)
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
        """
        verify_api_token(request)
        old_path = safe_path(base_dir, old_file_path)
        new_path = safe_path(base_dir, new_file_path)
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

    @app.get("/read/")
    async def read_file(
        request: Request,
        file_path: str = Query(..., description="Path to the file to read"),
    ):
        """
        Reads the content of a specified file.
        """
        verify_api_token(request)
        target_path = safe_path(base_dir, file_path)
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

    @app.get("/list/")
    async def list_files(
        request: Request,
        path: Optional[str] = Query(None, description="Path to list (optional)"),
    ):
        """
        Lists files and directories in a specified path.
        """
        verify_api_token(request)
        target_path = safe_path(base_dir, path)
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
