from .conversion_data import *
from dateutil.parser import parse
import re, string
from datetime import datetime


bangla_to_english_digits = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
english_to_bangla_digits = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def separate_year(year_str):
    """
    Convert a Bengali or English year string (with possible Bengali digits)
    into a tuple consisting of:
        • num1 → the century part (e.g., 1900)
        • num2 → the year part   (e.g.,   23)
    Returns (num1, num2).  If conversion fails, returns (None, None).
    """
    english_year_str = str(year_str).translate(bangla_to_english_digits)
    try:
        english_year_int = int(english_year_str)
        num1 = (english_year_int // 100) * 100
        num2 = english_year_int % 100
        return num1, num2
    except ValueError:
        print(f"Warning: Could not parse year '{year_str}' as integer.")
        return None, None


def extract_date_components_bangla(bangla_date):
    """
    Parse a Bangla date string, convert any Bengali digits/month names to
    English, and return the components:
        • day   → Bangla digits
        • month → Bangla month name
        • year  → Bangla digits
    On failure, returns a descriptive error string.
    """
    bangla_to_english_digits = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    english_to_bangla_digits = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

    try:
        for bangla_month, english_month in bangla_months.items():
            bangla_date = bangla_date.replace(bangla_month, english_month)

        bangla_date = bangla_date.translate(bangla_to_english_digits)
        parsed_date = parse(bangla_date, dayfirst=True, fuzzy=True)
        day = str(parsed_date.day).translate(english_to_bangla_digits)
        month = list(bangla_months.keys())[list(bangla_months.values()).index(parsed_date.strftime("%B"))]
        year = str(parsed_date.year).translate(english_to_bangla_digits)
        return day, month, year
    except Exception as e:
        return f"Error: {str(e)}"


def bangla_to_english_number(input_number_str):
    """
    Convert a numeric string containing Bengali or English digits (accepts
    commas, decimal points, and minus signs) into a Python int or float.
    Returns None if conversion is not possible.
    """
    if not isinstance(input_number_str, str):
        input_number_str = str(input_number_str)

    cleaned_str = input_number_str.replace('−', '-').replace(',', '')
    english_str = cleaned_str.translate(bangla_to_english_digits)

    try:
        if '.' in english_str:
            return float(english_str)
        else:
            return int(english_str)
    except ValueError:
        print(f"Warning: Could not convert '{input_number_str}' to English number.")
        return None


def remove_extra_spaces(input_text):
    """
    Collapse multiple consecutive whitespace characters into a single space
    and trim leading/trailing spaces.
    """

    text = re.sub(r'\s+', ' ', input_text).strip()
    if "টা টা" in text:
        text = text.replace("টা টা", "টা")
    return text


def convert_decimal_to_words(decimal_part):
    """
    Convert the fractional portion of a number (e.g. 75 in 0.75) into its
    English word representation using the `englishNum` mapping.
    """
    decimal_str = str(decimal_part)
    decimal_words = " ".join(englishNum[int(digit)] for digit in decimal_str if int(digit) in englishNum)
    return decimal_words


def get_bangla_time_period(time_str):
    """
    Given a time string (Bangla or English digits, optional AM/PM), return
    the Bangla period of the day:

        ভোর (3–6)  |  সকাল (6–12) | দুপুর (12–15)
        বিকেল (15–18) | সন্ধ্যা (18–20) | রাত (20–3)

    If parsing fails, returns 'ভুল সময় বিন্যাস'.
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
    Remove common Bengali and English punctuation marks from `text` and
    collapse any resulting multiple spaces into one.
    """
    bengali_punctuation = "।‘’“”"
    punctuation_to_remove = string.punctuation + bengali_punctuation + "-"
    translation_table = str.maketrans('', '', punctuation_to_remove)
    cleaned_text = text.translate(translation_table)
    cleaned_text = ' '.join(cleaned_text.split())
    return cleaned_text



def translate_english_word(sentence):
    """
    Replace English words in a sentence with their Bengali phonetic
    equivalents using the `english_to_bengali_phonetic_map` mapping.
    """
    words = sentence.split()
    translated_words = [
        english_to_bengali_phonetic_map.get(word.lower(), word)
        for word in words
    ]
    return " ".join(translated_words)
