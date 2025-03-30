##   AION.py

This file defines the main API logic for the AION RWX project, providing functionalities for interacting with the local file system. It includes endpoints for listing files, reading file content, and executing whitelisted shell commands. The API employs token-based authentication and implements security measures such as path validation and command whitelisting.

**Code Explanation:**

* **Imports:** The script imports necessary modules from FastAPI for building the API, Pydantic for data validation, `os` and `shutil` for file system operations, `subprocess` for executing shell commands, `logging` for activity tracking, and `json` for handling JSON data. It also imports configuration variables from `config.py`.
* **FastAPI Application Initialization:** An instance of the FastAPI application is created with the title "GPTRWXAPI".
* **Logging Setup:** A log directory is created, and basic logging is configured to record API activity in `activity.log`.
* **Attachment Directory:** An `attachments` directory is created for potential file uploads.
* **`verify_api_token` Function:** This function checks for the presence and validity of the API token in the request headers, ensuring only authorized access.
* **`safe_path` Function:** This function takes a sub-path as input and ensures that the resulting full path remains within the designated `BASE_DIRECTORY`, preventing unauthorized access to other parts of the file system.
* **`load_whitelist` Function:** This function reads the `whitelist.json` file and loads the list of allowed commands.
* **`ALLOWED_COMMANDS` Variable:** This variable stores the list of allowed commands loaded from the whitelist.
* **`is_command_allowed` Function:** This function checks if a given command is present in the `ALLOWED_COMMANDS` list. It allows for multi-level command chaining and also permits the execution of scripts with specific extensions like `.sh`, `.py`, etc.
* **`/list` Endpoint:** This GET endpoint lists all files and directories within a specified path. It first verifies the API token and then uses the `safe_path` function to ensure the path is valid.
* **`/read` Endpoint:** This GET endpoint reads the content of a specified file. It verifies the API token and uses `safe_path` to validate the file path before reading and returning the content.
* **`CommandRequest` Pydantic Model:** This model defines the expected structure for the request body of the `/execute` endpoint, which should contain a `command` string.
* **`/execute` Endpoint:** This POST endpoint executes a command provided in the request body. It verifies the API token and checks if the command is allowed using the `is_command_allowed` function before executing it using the `subprocess` module. The output (both stdout and stderr) and the status of the command execution are returned.
