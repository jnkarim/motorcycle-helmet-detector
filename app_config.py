"""
Configuration file for Helmet Detection System
"""
import os

# Model Configuration
MODEL_PATH = "helmet_best.pt"  # Your YOLO model path

# Class IDs (adjust based on your trained model)
HELMET_ID = 0
NO_HELMET_ID = 1
PLATE_ID = 2
RIDER_ID = 3

# Class Names
CLASS_NAMES = {
    0: "Helmet",
    1: "No-Helmet",
    2: "Plate",
    3: "Rider"
}

# Colors (BGR format)
# Colors for visualization
COLOR_RIDER = (255, 0, 0)       # Blue
COLOR_NO_HELMET = (0, 0, 255)   # Red
COLOR_PLATE = (0, 255, 0) 

# File Paths
CSV_FILE = "violations.csv"
SAVE_DIR = "violations"
ERROR_LOG_FILE = "error_log.txt"

# Create save directory if it doesn't exist
os.makedirs(SAVE_DIR, exist_ok=True)

# Detection Parameters
DEFAULT_CONF_THRESHOLD = 0.4
DEFAULT_COOLDOWN_TIME = 10
DUPLICATE_WINDOW = 15  # seconds