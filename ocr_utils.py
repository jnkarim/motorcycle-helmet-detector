"""
OCR utilities stub - Not used for detection, only for language checking
(We're not doing OCR - just saving images for manual review)
"""
import subprocess
import os

def check_tesseract_languages():
    """Check available Tesseract languages (for reference only)"""
    try:
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        if not os.path.exists(tesseract_path):
            return ["Tesseract not found"]
        
        result = subprocess.run(
            [tesseract_path, '--list-langs'],
            capture_output=True, 
            text=True,
            timeout=5
        )
        
        langs = result.stdout.strip().split('\n')[1:]  # Skip "List of available languages"
        return langs if langs else ["No languages found"]
        
    except Exception as e:
        return [f"Error: {str(e)}"]