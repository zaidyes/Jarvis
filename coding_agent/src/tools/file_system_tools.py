"""
File system tools for interacting with files and directories within the generated_project/ directory.

This module provides utility functions for reading, writing, and listing files
within the generated project workspace, with proper error handling and path management.
"""

import os
from pathlib import Path


def read_file(path: str) -> str:
    """
    Read the content of a file within the generated_project/ directory.
    
    This function takes a relative path, joins it with the generated_project/ directory,
    reads the file content, and returns it as a string. Includes error handling for
    FileNotFoundError and other potential file reading issues.
    
    Args:
        path (str): Relative path to the file from the generated_project/ directory.
                   Can include subdirectories (e.g., "src/main.py" or "config/settings.json").
    
    Returns:
        str: The content of the file as a string.
    
    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the file cannot be read due to permission issues.
        UnicodeDecodeError: If the file contains invalid UTF-8 characters.
    
    Example:
        >>> content = read_file("src/main.py")
        >>> print(content)
        # File content will be printed
    """
    # Join the relative path with the generated_project directory
    full_path = os.path.join("generated_project", path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {full_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: Cannot read file {full_path}")
    except UnicodeDecodeError:
        raise UnicodeDecodeError(
            'utf-8', b'', 0, 1, 
            f"File contains invalid UTF-8 characters: {full_path}"
        )


def write_file(path: str, content: str) -> str:
    """
    Write content to a file within the generated_project/ directory.
    
    This function takes a relative path and content, creates any necessary subdirectories,
    writes the content to the file within the generated_project/ directory, and returns
    a success message. Automatically creates parent directories if they don't exist.
    
    Args:
        path (str): Relative path to the file from the generated_project/ directory.
                   Can include subdirectories (e.g., "src/main.py" or "config/settings.json").
        content (str): The content to write to the file.
    
    Returns:
        str: Success message indicating the file was written successfully.
    
    Raises:
        PermissionError: If the file cannot be written due to permission issues.
        OSError: If there are other filesystem-related errors.
    
    Example:
        >>> result = write_file("src/main.py", "print('Hello, World!')")
        >>> print(result)
        "Successfully wrote to generated_project/src/main.py"
    """
    # Join the relative path with the generated_project directory
    full_path = os.path.join("generated_project", path)
    
    try:
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(full_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write the content to the file
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return f"Successfully wrote to {full_path}"
        
    except PermissionError:
        raise PermissionError(f"Permission denied: Cannot write to file {full_path}")
    except OSError as e:
        raise OSError(f"Filesystem error while writing to {full_path}: {str(e)}")


def list_files(path: str = ".") -> str:
    """
    List all files and directories within a given path inside generated_project/.
    
    This function lists all files and directories within the specified path inside
    the generated_project/ directory and returns the list as a formatted string.
    Shows both files and directories with clear indicators.
    
    Args:
        path (str, optional): Relative path within generated_project/ to list.
                            Defaults to "." (root of generated_project/).
                            Can include subdirectories (e.g., "src" or "config").
    
    Returns:
        str: Formatted string listing all files and directories found.
             Directories are marked with "[DIR]", files with "[FILE]".
    
    Raises:
        FileNotFoundError: If the specified path does not exist.
        PermissionError: If the directory cannot be read due to permission issues.
    
    Example:
        >>> files = list_files()
        >>> print(files)
        # Lists all files and directories in generated_project/
        
        >>> files = list_files("src")
        >>> print(files)
        # Lists all files and directories in generated_project/src/
    """
    # Join the relative path with the generated_project directory
    full_path = os.path.join("generated_project", path)
    
    try:
        if not os.path.exists(full_path):
            return f"Path does not exist: {full_path}"
        
        if not os.path.isdir(full_path):
            return f"Path is not a directory: {full_path}"
        
        # Get all items in the directory
        items = os.listdir(full_path)
        
        if not items:
            return f"Directory is empty: {full_path}"
        
        # Sort items for consistent output
        items.sort()
        
        # Format the output
        result = f"Contents of {full_path}:\n"
        result += "-" * (len(f"Contents of {full_path}:") + 2) + "\n"
        
        for item in items:
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                result += f"[DIR]  {item}/\n"
            else:
                result += f"[FILE] {item}\n"
        
        return result.strip()
        
    except PermissionError:
        raise PermissionError(f"Permission denied: Cannot read directory {full_path}")
    except OSError as e:
        raise OSError(f"Filesystem error while listing {full_path}: {str(e)}")
