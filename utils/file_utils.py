import os
import json


def read_file(file_path):
    """Reads the content of a file and returns it."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def write_file(file_path, data):
    """Writes data to a file."""
    try:
        with open(file_path, 'w') as file:
            file.write(data)
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

def save_json(file_path, data):
    """Saves data as a JSON file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"An error occurred while saving the JSON file: {e}")

def load_json(file_path):
    """Loads a JSON file and returns the data."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"An error occurred while loading the JSON file: {e}")
        return None

import random
import string

def generate_random_string(length=8):
    """Generates a random string of uppercase letters and digits."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def validate_email(email):
    """Validates the email format."""
    import re
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

import logging

def setup_logger(log_level=logging.DEBUG):
    """Sets up a logger with the specified log level."""
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger

# Example usage
logger = setup_logger()
logger.info("This is an info message")
logger.error("This is an error message")

def to_snake_case(s):
    """Converts a string to snake_case."""
    s = s.replace(" ", "_")
    return s.lower()

def to_title_case(s):
    """Converts a string to title case."""
    return s.title()

def load_config():
    """Load configuration from a file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_config(config_data):
    """Save configuration data to a file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)


