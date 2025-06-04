# --- START OF FILE methods.py ---

from utills import *
from conversion_data import * # Assumed to exist and be correct
# from exteactor import * # Not needed directly here
from datetime import datetime
import re


def date_to_word(date):
    day, month, year = extract_date_components_bangla(date)
    word = ''
    first_half, second_half = separate_year(year)
    if first_half % 1000 == 0:
        num = first_half // 1000
        word = englishNum[num] + " " + thousand
    else:
        num = first_half // 100
        word = englishNum[num] + hundred_suffix

    if second_half != 0:
        word = word + " " + englishNum[second_half]

    word = day_name[day] + " " + month + " " + word
    return word


def year_to_word(year):
    word = ''
    first_half, second_half = separate_year(year)
    if first_half % 1000 == 0:
        num = first_half // 1000
        word = englishNum[num] + " " + thousand
    else:
        num = first_half // 100
        word = englishNum[num] + hundred_suffix

    if second_half != 0:
        word = word + " " + englishNum[second_half]

    return word


def convert_integer_to_words(number):
    if number == 0:
        return "শূন্য"

    word = ""
    if number >= 10 ** 7:  # কোটি
        crore_part = number // 10 ** 7
        word += convert_integer_to_words(crore_part) + " " + "কোটি"
        number %= 10 ** 7
    if number >= 10 ** 5:  # লক্ষ
        lakh_part = number // 10 ** 5
        word += " " + convert_integer_to_words(lakh_part) + " " + "লক্ষ"
        number %= 10 ** 5
    if number >= 10 ** 3:  # হাজার
        thousand_part = number // 10 ** 3
        word += " " + convert_integer_to_words(thousand_part) + " " + "হাজার"
        number %= 10 ** 3
    if number >= 100:  # শত
        hundred_part = number // 100
        word += " " + englishNum[hundred_part] + "শো"
        number %= 100
    if number > 0:  # Remaining less than 100
        word += " " + englishNum[number]

    return word


def number_to_word(num):
    global number, integer_part, decimal_part
    minus = 0
    if '-' in num:
        num = num.replace('-', '')
        minus = 1

    if '.' in num:
        integer_part, decimal_part = num.split('.')[0], num.split(".")[1]
        integer_part = bangla_to_english_number(integer_part)
        decimal_part = bangla_to_english_number(decimal_part)
    else:
        number = bangla_to_english_number(num)

    if "." not in num:
        word = convert_integer_to_words(number)
        if minus==1:
            return minus_suffix + ' ' + remove_extra_spaces(word.strip())
        else:
            return remove_extra_spaces(word.strip())

    else:
        word = convert_integer_to_words(integer_part)
        decimal_words = convert_decimal_to_words(decimal_part)
        word += " দশমিক " + decimal_words
        if minus == 1:
            return minus_suffix + ' ' +  remove_extra_spaces(word.strip())
        else:
            return remove_extra_spaces(word.strip())


def phone_number_to_word(number_str):
    """Converts a phone number string (already extracted) to digit-by-digit Bengali words."""
    number_str = str(number_str).strip()
    cleaned_number = ""
    has_plus = False

    if number_str.startswith('+'):
        has_plus = True
        number_str = number_str[1:] # Remove plus for now

    # Remove common separators and keep only digits
    cleaned_number = re.sub(r'[-._\s]', '', number_str)
    # Convert all digits to Bengali digits for consistent lookup in banglaNum
    cleaned_number = cleaned_number.translate(bangla_to_english_digits).translate(english_to_bangla_digits)

    if not cleaned_number.isdigit():
         print(f"Warning: Non-digit characters remaining in phone number '{number_str}' after cleaning.")
         return number_str # Return original if cleaning failed

    word = " ".join(banglaNum.get(digit, digit) for digit in cleaned_number)

    if has_plus:
        word = "প্লাস " + word + " "
    else: word = word + " "

    return word


def time_to_word(time_str, text=''):
    """
    Converts a time string to its normalized word form.
    It first determines the period (e.g. "সকাল", "রাত") and then parses the time.
    The cleaned time string (with Bengali digits translated and "টায়" removed) is used for parsing.
    """
    if not any(word in text for word in ["রাত", "সন্ধ্যা", "বিকেল", "দুপুর", "সকাল", "ভোর"]):
        period_word = get_bangla_time_period(time_str)
    else:
        period_word = ''

    # Convert Bengali digits to English
    bangla_to_english = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    cleaned = time_str.translate(bangla_to_english).strip()
    aakar = False
    if 'মিনিটে' in time_str:
        aakar = True
    # Remove unnecessary words and standardize format
    cleaned = re.sub(r'\s*টায়|\s*মিনিটে|\s*টায\s*', '', cleaned)
    cleaned = cleaned.replace("এ.এম.", "AM").replace("পিএম", "PM") \
        .replace("a.m.", "AM").replace("p.m.", "PM")

    # Determine if it's a 12-hour format
    is_12h = "AM" in cleaned or "PM" in cleaned

    try:
        # Attempt to parse using different time formats
        time_obj = None
        possible_formats = ["%I:%M:%S %p", "%I:%M %p", "%H:%M:%S", "%H:%M"]
        for fmt in possible_formats:
            try:
                time_obj = datetime.strptime(cleaned, fmt)
                break  # Stop if parsing is successful
            except ValueError:
                continue

        if time_obj is None:
            return "ভুল সময় বিন্যাস"

        # Use 12-hour clock if input is in 12h format
        if is_12h:
            # Convert hour using strftime("%I") which returns a zero-padded 12-hour format hour
            hour = int(time_obj.strftime("%I"))
        else:
            hour = time_obj.hour

        minute = time_obj.minute
        second = time_obj.second if time_obj.second else None

        # Convert numbers to Bangla words (assuming number_to_word converts string numbers to Bangla words)
        hour_word = number_to_word(str(hour))
        minute_word = number_to_word(str(minute))
        second_word = number_to_word(str(second)) if second is not None else None

        # Build the final output string
        result = period_word + " " + hour_word + " " + "টা"
        if minute > 0:
            result += " " + minute_word + " " + ("মিনিটে" if aakar or not second else "মিনিট")
        if second:
            result += " " + second_word + " " + "সেকেন্ড"

        return result

    except Exception as e:
        print("Error:", e)
        return "ভুল সময় বিন্যাস"

def taka_to_word(taka_str):
    """Converts extracted Taka string (e.g., ৳৫০০, ২৫০ টাকা, ৳১০ লক্ষ) to words."""
    original_taka_str = taka_str
    taka_str = taka_str.strip()
    suffix = " টাকা" # Default suffix

    # Check for specific suffixes
    if taka_str.endswith('টাকার'):
        suffix = " টাকার"
        taka_str = taka_str[:-5].strip() # Remove 'টাকার'
    elif taka_str.endswith('টাকা'):
        taka_str = taka_str[:-4].strip() # Remove 'টাকা'

    # Handle special units like লক্ষ, কোটি often appearing after ৳
    unit = ""
    if taka_str.endswith('লক্ষ'):
        unit = " লক্ষ"
        taka_str = taka_str.replace('লক্ষ', '')
    elif taka_str.endswith('কোটি'):
        unit = " কোটি"
        taka_str = taka_str.replace('কোটি', '')

    # Remove symbol and commas
    taka_str = taka_str.replace('৳', '').replace(',', '').strip()

    # Convert the numeric part
    num_word = number_to_word(taka_str)

    if num_word == taka_str: # If number conversion failed
        return original_taka_str

    # Combine: number word + optional unit + suffix
    return remove_extra_spaces(num_word + unit + suffix)


def percentage_to_word(perc_str):
    """Converts percentage string (e.g., ১০%, ১৫.৫ শতাংশ) to words."""
    original_perc_str = perc_str
    perc_str = perc_str.strip()
    # Remove suffix
    num_str = perc_str.replace('%', '').replace('শতাংশ', '').strip()

    num_word = number_to_word(num_str)

    if num_word == num_str: # Conversion failed
        return original_perc_str

    return remove_extra_spaces(num_word + " " + percentage_suffix)


def temperature_to_word(temp_str):
    """Converts temperature string (e.g., ৩০°C, ৩৫.৫ ডিগ্রি সেলসিয়াস) to words."""
    original_temp_str = temp_str
    temp_str = temp_str.strip()

    # Extract number part using regex, handling negative signs and decimals
    match = re.match(r'([-−]?\s*[০-৯0-9,]+(?:\.[০-৯0-9]+)?)', temp_str)
    if not match:
        return original_temp_str  # Cannot find number part

    num_str = match.group(1).strip()

    # Check if there is a decimal point and convert parts separately
    if '.' in num_str:
        integer_part, fractional_part = num_str.split('.', 1)
        integer_word = number_to_word(integer_part)
        fractional_word = phone_number_to_word(fractional_part)
        num_word = integer_word + " দশমিক " + fractional_word
    else:
        num_word = number_to_word(num_str)

    # Determine the unit based on context in the original string
    unit_word = " ডিগ্রি"  # Default unit
    temp_str_lower = temp_str.lower()
    if 'সেলসিয়াস' in temp_str_lower or '°c' in temp_str_lower or ' সে.' in temp_str_lower:
        unit_word = " ডিগ্রি সেলসিয়াস"
    elif 'ফারেনহাইট' in temp_str_lower or '°f' in temp_str_lower:
        unit_word = " ডিগ্রি ফারেনহাইট"
    elif 'কেলভিন' in temp_str_lower or '°k' in temp_str_lower:
        unit_word = " ডিগ্রি কেলভিন"

    return remove_extra_spaces(num_word + unit_word)


def ordinal_to_word(ord_str):
    """Converts ordinal string (e.g., ১ম, 2nd, ১০,০০০তম) to words."""
    ord_str = ord_str.strip()

    # Simple lookup first
    if ord_str in ordinal_normalization_map:
        return ordinal_normalization_map[ord_str]

    # Handle complex cases like 10,000তম
    match = re.match(r'([০-৯0-9,]+)(?:ম|য়|লা|রা|শে|ই|র্থ|তম|st|nd|rd|th)', ord_str, re.IGNORECASE)
    if match:
        num_part = match.group(1)
        suffix = ord_str[len(num_part):] # Get the original suffix

        num_word = number_to_word(num_part) # Convert number part (handles commas)

        # Determine appropriate Bengali suffix word if possible
        bengali_suffix_word = "তম" # Default fallback
        if suffix.lower() in ['st', 'লা']: bengali_suffix_word = "" # 'প্রথম' usually handles this, or 'পহেলা' if needed
        elif suffix.lower() in ['nd', 'রা']: bengali_suffix_word = "" # 'দ্বিতীয়', 'দোসরা'
        elif suffix.lower() in ['rd', 'য়', 'শে']: bengali_suffix_word = "" # 'তৃতীয়', 'তেসরা'

        if num_word != num_part: # Check if conversion happened
             # Avoid double suffix if num_word already implies ordinal (e.g., 'প্রথম')
             if num_word not in ordinal_normalization_map.values():
                 # Basic logic: For large numbers ending in তম/th, just use the number word + তম
                  if suffix.lower() in ['তম', 'th']:
                     return num_word + " তম"
                  # Add more sophisticated suffix logic here if needed
             return num_word # Assume number_to_word produced the correct ordinal word


    # Fallback
    return ord_str
# --- END OF FILE methods.py ---