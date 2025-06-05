from .utils import *
from .conversion_data import *
from datetime import datetime
import re


def date_to_word(date):
    """
    Converts a date string to its Bengali word representation.
    Handles day, month, and year components separately.
    """
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
    """
    Converts a year number to its Bengali word representation.
    Handles splitting the year into two parts for proper conversion.
    """
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
    """
    Converts an integer number to Bengali words.
    Handles large numbers up to crore with proper unit suffixes.
    """
    if number == 0:
        return "শূন্য"

    word = ""
    if number >= 10 ** 7:
        crore_part = number // 10 ** 7
        word += convert_integer_to_words(crore_part) + " " + "কোটি"
        number %= 10 ** 7
    if number >= 10 ** 5:
        lakh_part = number // 10 ** 5
        word += " " + convert_integer_to_words(lakh_part) + " " + "লক্ষ"
        number %= 10 ** 5
    if number >= 10 ** 3:
        thousand_part = number // 10 ** 3
        word += " " + convert_integer_to_words(thousand_part) + " " + "হাজার"
        number %= 10 ** 3
    if number >= 100:
        hundred_part = number // 100
        word += " " + englishNum[hundred_part] + "শো"
        number %= 100
    if number > 0:
        word += " " + englishNum[number]

    return word


def number_to_word(num):
    """
    Converts a number string (integer or decimal) to Bengali words.
    Handles negative numbers and decimal points.
    """
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
    """
    Converts a phone number string to digit-by-digit Bengali words.
    Handles international format (+ prefix) and common separators.
    """
    number_str = str(number_str).strip()
    cleaned_number = ""
    has_plus = False

    if number_str.startswith('+'):
        has_plus = True
        number_str = number_str[1:]

    cleaned_number = re.sub(r'[-._\s]', '', number_str)
    cleaned_number = cleaned_number.translate(bangla_to_english_digits).translate(english_to_bangla_digits)

    if not cleaned_number.isdigit():
         print(f"Warning: Non-digit characters remaining in phone number '{number_str}' after cleaning.")
         return number_str

    word = " ".join(banglaNum.get(digit, digit) for digit in cleaned_number)

    if has_plus:
        word = "প্লাস " + word + " "
    else: word = word + " "

    return word


def time_to_word(time_str, text=''):
    """
    Converts a time string to its normalized Bengali word form.
    Handles 12/24 hour formats, AM/PM indicators, and time periods (morning, evening).
    """
    if not any(word in text for word in ["রাত", "সন্ধ্যা", "বিকেল", "দুপুর", "সকাল", "ভোর"]):
        period_word = get_bangla_time_period(time_str)
    else:
        period_word = ''

    bangla_to_english = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    cleaned = time_str.translate(bangla_to_english).strip()
    aakar = False
    if 'মিনিটে' in time_str:
        aakar = True

    cleaned = re.sub(r'\s*টায়|\s*মিনিটে|\s*টায\s*', '', cleaned)
    cleaned = cleaned.replace("এ.এম.", "AM").replace("পিএম", "PM") \
        .replace("a.m.", "AM").replace("p.m.", "PM")

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

        if is_12h:
            hour = int(time_obj.strftime("%I"))
        else:
            hour = time_obj.hour

        minute = time_obj.minute
        second = time_obj.second if time_obj.second else None

        hour_word = number_to_word(str(hour))
        minute_word = number_to_word(str(minute))
        second_word = number_to_word(str(second)) if second is not None else None

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
    """
    Converts a currency string (Taka) to Bengali words.
    Handles different formats including symbols, suffixes, and large units (lakh, crore).
    """
    original_taka_str = taka_str
    taka_str = taka_str.strip()
    suffix = " টাকা"

    if taka_str.endswith('টাকার'):
        suffix = " টাকার"
        taka_str = taka_str[:-5].strip()
    elif taka_str.endswith('টাকা'):
        taka_str = taka_str[:-4].strip()

    unit = ""
    if taka_str.endswith('লক্ষ'):
        unit = " লক্ষ"
        taka_str = taka_str.replace('লক্ষ', '')
    elif taka_str.endswith('কোটি'):
        unit = " কোটি"
        taka_str = taka_str.replace('কোটি', '')

    taka_str = taka_str.replace('৳', '').replace(',', '').strip()

    num_word = number_to_word(taka_str)

    if num_word == taka_str:
        return original_taka_str

    return remove_extra_spaces(num_word + unit + suffix)


def percentage_to_word(perc_str):
    """
    Converts a percentage string to Bengali words.
    Handles both % symbol and 'শতাংশ' suffix.
    """
    original_perc_str = perc_str
    perc_str = perc_str.strip()
    num_str = perc_str.replace('%', '').replace('শতাংশ', '').strip()

    num_word = number_to_word(num_str)

    if num_word == num_str:
        return original_perc_str

    return remove_extra_spaces(num_word + " " + percentage_suffix)


def temperature_to_word(temp_str):
    """
    Converts a temperature string to Bengali words.
    Handles different temperature units (Celsius, Fahrenheit, Kelvin).
    """
    original_temp_str = temp_str
    temp_str = temp_str.strip()

    match = re.match(r'([-−]?\s*[০-৯0-9,]+(?:\.[০-৯0-9]+)?)', temp_str)
    if not match:
        return original_temp_str

    num_str = match.group(1).strip()

    if '.' in num_str:
        integer_part, fractional_part = num_str.split('.', 1)
        integer_word = number_to_word(integer_part)
        fractional_word = phone_number_to_word(fractional_part)
        num_word = integer_word + " দশমিক " + fractional_word
    else:
        num_word = number_to_word(num_str)

    unit_word = " ডিগ্রি"
    temp_str_lower = temp_str.lower()
    if 'সেলসিয়াস' in temp_str_lower or '°c' in temp_str_lower or ' সে.' in temp_str_lower:
        unit_word = " ডিগ্রি সেলসিয়াস"
    elif 'ফারেনহাইট' in temp_str_lower or '°f' in temp_str_lower:
        unit_word = " ডিগ্রি ফারেনহাইট"
    elif 'কেলভিন' in temp_str_lower or '°k' in temp_str_lower:
        unit_word = " ডিগ্রি কেলভিন"

    return remove_extra_spaces(num_word + unit_word)


def ordinal_to_word(ord_str):
    """
    Converts an ordinal number string to Bengali words.
    Handles both Bengali and English ordinal suffixes.
    """
    ord_str = ord_str.strip()

    if ord_str in ordinal_normalization_map:
        return ordinal_normalization_map[ord_str]

    match = re.match(r'([০-৯0-9,]+)(?:ম|য়|লা|রা|শে|ই|র্থ|তম|st|nd|rd|th)', ord_str, re.IGNORECASE)
    if match:
        num_part = match.group(1)
        suffix = ord_str[len(num_part):]

        num_word = number_to_word(num_part)

        bengali_suffix_word = "তম"
        if suffix.lower() in ['st', 'লা']: bengali_suffix_word = ""
        elif suffix.lower() in ['nd', 'রা']: bengali_suffix_word = ""
        elif suffix.lower() in ['rd', 'য়', 'শে']: bengali_suffix_word = ""

        if num_word != num_part:
             if num_word not in ordinal_normalization_map.values():
                  if suffix.lower() in ['তম', 'th']:
                     return num_word + " তম"
             return num_word

    return ord_str


def distance_to_word(text):
    """
    Converts distance abbreviations or symbols in the input text to their full Bangla word equivalents.

    - Uses `unit_to_bangla_map` to replace short forms (e.g., "cm", "'", '"') with Bangla terms (e.g., "সেন্টিমিটার", "ফুট", "ইঞ্চি").
    - Normalizes numeric digits using `normalizer.normalize_numbers`.

    Returns:
        str: Text with unit symbols replaced by full Bangla words and digits normalized.
    """
    sorted_units = sorted(unit_to_bangla_map.items(), key=lambda x: len(x[0]), reverse=True)
    output = text
    for key, value in sorted_units:
        if key in text:
            output = output.replace(key, f' {value} ')

    pattern = r'(?<![0-9০-৯.,৳])(?:[-−]?)([0-9০-৯]+(?:,[0-9০-৯]{3})*(?:\.[0-9০-৯]+)?|[0-9০-৯]+\.[0-9০-৯]+)(?![0-9০-৯.,%])'
    matches = re.findall(pattern, output)

    sorted_matches = sorted(list(set(matches)), key=len, reverse=True)

    for sm in sorted_matches:
        output = output.replace(sm, number_to_word(sm))

    return output



