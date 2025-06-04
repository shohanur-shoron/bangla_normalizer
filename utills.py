# --- START OF FILE utills.py ---

from conversion_data import *
from dateutil.parser import parse, ParserError
import re, string
from datetime import datetime

# Translation maps
bangla_to_english_digits = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
english_to_bangla_digits = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

def separate_year(year_str):
    """Converts Bengali/English year string to English int, then separates."""
    english_year_str = str(year_str).translate(bangla_to_english_digits)
    try:
        english_year_int = int(english_year_str)
        num1 = (english_year_int // 100) * 100
        num2 = english_year_int % 100
        return num1, num2
    except ValueError:
        # Handle cases where year might not be purely numeric after extraction (shouldn't happen with good regex)
        print(f"Warning: Could not parse year '{year_str}' as integer.")
        return None, None


def extract_date_components_bangla(bangla_date):
    bangla_to_english_digits = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    english_to_bangla_digits = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

    try:
        for bangla_month, english_month in bangla_months.items():
            bangla_date = bangla_date.replace(bangla_month, english_month)

        # Convert Bangla digits to English digits
        bangla_date = bangla_date.translate(bangla_to_english_digits)

        # Parse the processed date
        parsed_date = parse(bangla_date, dayfirst=True, fuzzy=True)
        day = str(parsed_date.day).translate(english_to_bangla_digits)
        month = list(bangla_months.keys())[list(bangla_months.values()).index(parsed_date.strftime("%B"))]
        year = str(parsed_date.year).translate(english_to_bangla_digits)
        return day, month, year
    except Exception as e:
        return f"Error: {str(e)}"

def bangla_to_english_number(input_number_str):
    """Converts a string containing Bengali or English digits (potentially with ',', '.', '-', '−') to a float or int."""
    if not isinstance(input_number_str, str):
        input_number_str = str(input_number_str)

    # Normalize negative signs and remove commas
    cleaned_str = input_number_str.replace('−', '-').replace(',', '')
    # Convert Bengali digits to English
    english_str = cleaned_str.translate(bangla_to_english_digits)

    try:
        if '.' in english_str:
            return float(english_str)
        else:
            return int(english_str)
    except ValueError:
        # Handle cases where the input might not be a valid number after cleaning
        print(f"Warning: Could not convert '{input_number_str}' to English number.")
        return None # Or raise an error, or return 0


def remove_extra_spaces(input_text):
    """Removes extra whitespace."""
    return re.sub(r'\s+', ' ', input_text).strip()


def convert_decimal_to_words(decimal_part):
    decimal_str = str(decimal_part)
    decimal_words = " ".join(englishNum[int(digit)] for digit in decimal_str if int(digit) in englishNum)
    return decimal_words


def get_bangla_time_period(time_str):
    """
    Returns the Bangla time period (e.g., "সকাল", "রাত") based on the hour.
    """
    bangla_to_english = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    cleaned = time_str.translate(bangla_to_english).strip()
    cleaned = re.sub(r'\s*টায়\s*', '', cleaned)
    cleaned = cleaned.replace("এ.এম.", "AM").replace("পিএম", "PM").replace("a.m.", "AM").replace("p.m.", "PM")

    is_12h = "AM" in cleaned or "PM" in cleaned

    try:
        time_obj = None
        possible_formats = ["%I:%M:%S %p", "%I:%M %p", "%H:%M:%S", "%H:%M"]

        for fmt in possible_formats:
            try:
                time_obj = datetime.strptime(cleaned, fmt)
                break
            except ValueError:
                continue

        if time_obj is None:
            return "ভুল সময় বিন্যাস"

        hour = time_obj.hour

        if 3 <= hour < 6:
            return "ভোর"
        elif 6 <= hour < 12:
            return "সকাল"
        elif 12 <= hour < 15:
            return "দুপুর"
        elif 15 <= hour < 18:
            return "বিকেল"
        elif 18 <= hour < 20:
            return "সন্ধ্যা"
        else:
            return "রাত"

    except Exception:
        return "ভুল সময় বিন্যাস"



def remove_punctuation(text: str) -> str:
    """
    Removes common Bengali and English punctuation marks from a string.

    Args:
        text: The input string.

    Returns:
        The string with specified punctuation removed.
    """
    # Define Bengali punctuation (add more if needed)
    bengali_punctuation = "।‘’“”" # Dāri, Bengali quotes

    # Combine with standard English punctuation from string module and other common symbols
    # string.punctuation includes: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    # We add Bengali punctuation and ensure common ones like hyphens are covered.
    punctuation_to_remove = string.punctuation + bengali_punctuation + "-"

    # Create a translation table mapping each punctuation character to None (for deletion)
    translation_table = str.maketrans('', '', punctuation_to_remove)

    # Apply the translation to remove the punctuation
    cleaned_text = text.translate(translation_table)

    # Optional: Remove potential multiple spaces resulting from punctuation removal
    cleaned_text = ' '.join(cleaned_text.split())

    return cleaned_text



def bangla_to_ipa_converter(sentence):
    sentence = remove_punctuation(sentence)
    ipa_output = ""
    i = 0
    # Determine maximum length of any conjunct key:
    max_conj_length = max(len(key) for key in bangla_conjuncts_to_ipa) if bangla_conjuncts_to_ipa else 0
    while i < len(sentence):
        # Try to match the longest possible conjunct from our list:
        match_found = False
        for l in range(max_conj_length, 0, -1):
            if i + l <= len(sentence):
                segment = sentence[i:i+l]
                if segment in bangla_conjuncts_to_ipa:
                    ipa_output += bangla_conjuncts_to_ipa[segment]
                    i += l
                    match_found = True
                    break
        if not match_found:
            char = sentence[i]
            # Look up individual character in our simple mapping
            ipa_output += bangla_to_ipa.get(char, char)
            i += 1
    return ipa_output


def translate_english_word(sentence):    
    # Split the sentence into words
    words = sentence.split()
    
    # Replace any word found in the map (case insensitive)
    translated_words = [
        english_to_bengali_phonetic_map.get(word.lower(), word)
        for word in words
    ]
    
    # Join the translated words back into a sentence
    return " ".join(translated_words)