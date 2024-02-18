import os
import json
from pathlib import Path

PROJECT_PATH = os.path.join(Path(__file__).parent.parent)
RESOURCES_PATH = os.path.join(PROJECT_PATH, "resources")
INPUT_FILES = os.path.join(PROJECT_PATH, "input_files")

# --- CATEGORIES ---
with open(os.path.join(RESOURCES_PATH, "categories.json"), "r") as file:
    CATEGORIES = json.loads(file.read())

PERSONAL_CATEGORIES = CATEGORIES["PERSONAL_CATEGORIES"]
HOME_CATEGORIES = CATEGORIES["HOME_CATEGORIES"]

# --- BANK FORMATS ---
with open(os.path.join(RESOURCES_PATH, "banks_format.json"), "r") as file:
    BANK_FORMATS = json.loads(file.read())
