import json
import os
from typing import Any, Dict, List, Optional

CONFIG_FILE = os.path.join('static', 'data', 'config.json')


def read_config() -> Dict[str, Any]:
    """
    Read the configuration from the JSON file.

    Returns:
        Dict[str, Any]: The configuration data
    """
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def write_config(data: Dict[str, Any]) -> bool:
    """
    Write data to the configuration file.

    Args:
        data (Dict[str, Any]): The data to write

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing to config file: {str(e)}")
        return False


def update_config(key: str, value: Any) -> bool:
    """
    Update a specific key in the configuration.

    Args:
        key (str): The key to update
        value (Any): The new value

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config = read_config()
        config[key] = value
        return write_config(config)
    except Exception as e:
        print(f"Error updating config: {str(e)}")
        return False


def get_available_models() -> List[str]:
    """
    Get the list of available models.

    Returns:
        List[str]: List of model names
    """
    config = read_config()
    return config.get('models', {}).get('available_models', [])


def get_default_model() -> str:
    """
    Get the default model.

    Returns:
        str: Default model name
    """
    config = read_config()
    return config.get('models', {}).get('default_model', '')


def get_status_color(status: str) -> str:
    """
    Get the color for a specific status.

    Args:
        status (str): The status to get the color for

    Returns:
        str: The color code
    """
    config = read_config()
    # Default to gray if not found
    return config.get('status_colors', {}).get(status, '#6c757d')


def get_allowed_extensions() -> List[str]:
    """
    Get the list of allowed file extensions.

    Returns:
        List[str]: List of allowed extensions
    """
    config = read_config()
    return config.get('file_types', {}).get('allowed_extensions', [])


def get_max_file_size() -> int:
    """
    Get the maximum allowed file size in MB.

    Returns:
        int: Maximum file size in MB
    """
    config = read_config()
    return config.get('file_types', {}).get('max_size_mb', 100)
