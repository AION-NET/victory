#   Technical Summary of AION RWX Project Code

This document provides a descriptive professional summary of the code within each Python file of the AION RWX project, along with explanations of the code's functionality.

## AION.py

**Summary:** This file defines the main API logic for the AION RWX project, providing functionalities for interacting with the local file system. It includes endpoints for listing files, reading file content, and executing whitelisted shell commands. The API employs token-based authentication and implements security measures such as path validation and command whitelisting.

**Code Explanation:**

* **Imports:** The script imports necessary modules from FastAPI for building the API, Pydantic for data validation, os and shutil for file system operations, subprocess for executing shell commands, logging for activity tracking, and json for handling JSON data. It also imports configuration variables from `config.py`.
* **FastAPI Application Initialization:** An instance of the FastAPI application is created with the title "GPTRWXAPI".
* **Logging Setup:** A log directory is created, and basic logging is configured to record API activity in `activity.log`.
* **Attachment Directory:** An `attachments` directory is created for potential file uploads.
* **`verify_api_token` Function:** This function checks for the presence and validity of the API token in the request headers, ensuring only authorized access.
* **`safe_path` Function:** This function takes a sub-path as input and ensures that the resulting full path remains within the designated `BASE_DIRECTORY`, preventing unauthorized access to other parts of the file system.
* **`load_whitelist` Function:** This function reads the `whitelist.json` file and loads the list of allowed commands.
* **`ALLOWED_COMMANDS` Variable:** This variable stores the list of allowed commands loaded from the whitelist.
* **`is_command_allowed` Function:** This function checks if a given command is present in the `ALLOWED_COMMANDS` list. It allows for multi-level command chaining and also permits the execution of scripts with specific extensions like `.sh`, `.py`, etc.
* `/list` Endpoint:** This GET endpoint lists all files and directories within a specified path. It first verifies the API token and then uses the `safe_path` function to ensure the path is valid.
* `/read` Endpoint:** This GET endpoint reads the content of a specified file. It verifies the API token and uses `safe_path` to validate the file path before reading and returning the content.
* `CommandRequest` Pydantic Model:** This model defines the expected structure for the request body of the `/execute` endpoint, which should contain a `command` string.
* `/execute` Endpoint:** This POST endpoint executes a command provided in the request body. It verifies the API token and checks if the command is allowed using the `is_command_allowed` function before executing it using the `subprocess` module. The output (both stdout and stderr) and the status of the command execution are returned.

## keygen.py

**Summary:** This script is responsible for generating a secure API key and saving it to the `.env` file. It checks if an API key already exists; if not, it generates a new one.

**Code Explanation:**

* **Imports:** It imports the `os` module for interacting with the operating system, the `load_dotenv` and `set_key` functions from the `dotenv` library for managing environment variables, and the `secrets` module for generating cryptographically secure random numbers.
* **Environment Variable Loading:** `load_dotenv()` loads environment variables from the `.env` file into the script's environment.
* `.env` File Path:** The `ENV_FILE` variable stores the name of the environment file (`.env`).
* API Token Check:** It retrieves the value of the `API_TOKEN` environment variable using `os.getenv()`.
* `generate_api_key` Function:** This function uses `secrets.token_hex(32)` to generate a random 64-character hexadecimal string, which serves as a secure API key.
* `save_api_key` Function:** This function uses `set_key(ENV_FILE, "API_TOKEN", api_key)` to write the provided `api_key` to the `.env` file, setting the `API_TOKEN` environment variable.
* API Key Generation and Saving Logic:** The script checks if `API_TOKEN` is already set. If not, it calls `generate_api_key()` to create a new key and `save_api_key()` to store it in the `.env` file. If the `API_TOKEN` already exists, it prints a message indicating that the existing key has been loaded.

## config.py

**Summary:** This file handles the configuration settings for the AION RWX API. It loads environment variables from a `.env` file and defines important constants like the base directory for file operations and the API token. It also includes logic to generate and save an API key if one doesn't exist.

**Code Explanation:**

* **Imports:** It imports the `os` module for operating system interactions, `load_dotenv` and `set_key` from the `dotenv` library for managing environment variables, and `secrets` for secure API key generation.
* **Environment Variable Loading:** `load_dotenv()` loads variables from the `.env` file.
* `.env` File Path:** `ENV_FILE` stores the name of the environment file.
* `BASE_DIRECTORY` Definition:** This line determines the base directory for file operations by getting the directory of the current script's absolute path. This ensures that the API primarily interacts within its deployment folder.
* API Token Loading:** It attempts to load the `API_TOKEN` from the environment variables using `os.getenv()`.
* `generate_api_key` Function:** This function (identical to the one in `keygen.py`) generates a secure API key using `secrets.token_hex(32)`.
* `save_api_key` Function:** This function (identical to the one in `keygen.py`) saves the generated API key to the `.env` file.
* API Key Generation Logic:** Similar to `keygen.py`, if `API_TOKEN` is not found in the environment, a new one is generated and saved. Otherwise, the existing one is loaded.
* `validate_directory` Function:** This function checks if the `BASE_DIRECTORY` exists. If it doesn't, it raises a `ValueError`. If it exists, it prints a confirmation message.
* Directory Validation:** The `validate_directory()` function is called to ensure the working directory is set up correctly.

## app.py

**Summary:** This file appears to be an older version or an alternative entry point for the RWX API. It provides similar functionalities to `AION.py`, including listing files, reading file content, and executing a predefined set of allowed shell commands. It also implements token-based authentication and path validation.

**Code Explanation:**

* **Imports:** It imports necessary modules from FastAPI, Pydantic, os, shutil, subprocess, logging, and configuration variables from `config.py`. These are similar to the imports in `AION.py`.
* **FastAPI Application Initialization:** An instance of the FastAPI application is created with the title "GPTRWXAPI".
* **Logging and Attachment Directory Setup:** Similar to `AION.py`, it sets up logging to an `activity.log` file and creates an `attachments` directory.
* **`verify_api_token` Function:** This function is identical to the one in `AION.py`, performing API token verification from the request headers.
* **`safe_path` Function:** This function is also identical to the one in `AION.py`, ensuring that accessed paths are within the `BASE_DIRECTORY`.
* `/list` Endpoint:** This GET endpoint functions the same as in `AION.py`, listing files within a given path after token verification and path validation.
* `/read` Endpoint:** This GET endpoint also functions the same as in `AION.py`, reading the content of a specified file after security checks.
* `CommandRequest` Pydantic Model:** This model is identical to the one in `AION.py`, defining the expected structure for command execution requests.
* `/execute` Endpoint:** This POST endpoint allows the execution of a predefined list of commands. It verifies the API token and then checks if the requested command starts with any of the commands in the `allowed_commands` list. If allowed, it executes the command using `subprocess.check_output` and returns the output. If the command fails or is not in the allowed list, it raises an HTTPException. The list of allowed commands is hardcoded within this file, unlike `AION.py`, which loads it from `whitelist.json`.

## requirements.txt

**Summary:** This file lists the Python packages that are dependencies for the AION RWX project. It specifies the libraries that need to be installed for the project to run correctly.

**Content Explanation:**

This file contains a list of Python packages, one per line:

* `fastapi`: A modern, fast (high-performance), web framework for building APIs with Python.
* `uvicorn`: An ASGI server for running FastAPI applications.
* `pydantic`: A data validation and settings management library used by FastAPI.
* `python-dotenv`: A library to load environment variables from a `.env` file.
* `python-multipart`: A library to support handling multipart form data, which is often used for file uploads in web applications.

## whitelist.json

**Summary:** This file contains a JSON object that defines a list of allowed shell commands for the `/execute` endpoint in `AION.py`. This acts as a security measure to restrict the commands that can be executed by the API.

**Content Explanation:**

The file contains a single JSON object with a key named `"allowed_commands"`. The value associated with this key is a JSON array of strings. Each string in the array represents a command or a sequence of command parts that are considered safe to execute by the API. The `is_command_allowed` function in `AION.py` uses this list to determine if a requested command should be executed. The whitelist includes common commands for file system navigation, file manipulation, and running Python scripts, as well as Git commands and system utilities.

## README.md

**Summary:** This file serves as the main documentation for the AION RWX project. It provides an overview of the API, instructions on how to run the server, details about integrating with the OpenAI Actions API, and a description of the available API endpoints and their functionalities.

**Content Explanation:**

The `README.md` file includes the following key sections:

* **Project Title and Copyright:** Specifies the project name "AION RWX" and the copyright information.
* **Running the Server:** Provides instructions on how to install the necessary dependencies using `pip install -r requirements.txt` and how to start the server using `uvicorn app:app --reload --host 127.0.0.1 --port 8000`.
* **Integration with OpenAI Actions API:** Explains how to expose the API to the internet using `ngrok` for integration with OpenAI.
* **Deployment-Ready Features:** Lists the core functionalities of the API, including reading, writing, and executing files, security features, and compatibility with the OpenAI Actions API.
* **API Endpoint Descriptions:** Provides detailed information for each API endpoint:
    * **List Files:** `/list` (GET) - Describes how to list files in the deployment folder or the `/mnt/data` folder.
    * **Read a File:** `/read-file` (GET) - Explains how to read the content of a file.
    * **Upload a File:** `/upload` (POST) - Describes how to upload a file to the local folder.
    * **Download a File:** `/download` (GET) - Explains how to download a file from the local folder.
    * **Execute a Safe Command:** `/execute` (POST) - Details how to run whitelisted commands.
    * **Compress a Folder:** `/compress` (POST) - Explains how to compress a folder into a `.tar.gz` archive.
    * **Upload a File to the Context Window (Simulated):** `/upload-to-context` (POST) - Describes a simulated action.
    * **Trigger the "Continue ↵" Button (Simulated):** `/trigger-continue` (POST) - Describes another simulated action.
* **Security Layers:** Summarizes the security measures implemented, such as OpenAI Bearer Token Authentication, command whitelisting, path validation, and logging.
* **Summary of GPT-4 Agent Actions:** Provides a table listing each API action, its endpoint, HTTP method, and security status.
* **Next Steps:** Suggests further actions like deploying the API and registering the schema with OpenAI.
* **Custom Header:** Mentions the custom header `action-api-key` used for authentication.
* **Dev Setup:** Includes a link to ngrok.
* **OpenAPI Specification:** Contains the OpenAPI 3.1.0 specification for the API, defining the `/execute` and `/read` endpoints, their operations, request and response bodies, and security schemes.
* **Example Commands:** Shows example commands to run the server using `uvicorn` and `python3`.

## intro.md

**Summary:** This file appears to be a brief introductory markdown file for the AION RWX project, likely containing a link to an external resource.

**Content Explanation:**

The file contains a hyperlink to an OpenSea collection related to "aionrwx" and a heading indicating that prompts might be found in the description of that collection.
