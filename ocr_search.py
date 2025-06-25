import pytesseract
from PIL import Image
import sys
import os

def contains_word(image_path, word):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return word.lower() in text.lower(), text
    except Exception as e:
        print(f"OCR error for {image_path}: {e}")
        return False, ""

def scan_folder_for_word(folder, word):
    matches = []
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath) and fname.lower().endswith((".png", ".jpg", ".jpeg")):
            found, text = contains_word(fpath, word)
            if found:
                print(f"[MATCH] {fname}: contains '{word}'")
                matches.append((fname, text))
    print(f"Total matches for '{word}': {len(matches)}")
    return matches

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ocr_search.py <folder> <word>")
        sys.exit(1)
    folder = sys.argv[1]
    word = sys.argv[2]
    scan_folder_for_word(folder, word)
