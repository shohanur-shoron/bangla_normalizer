# --- START OF FILE exteactor.py ---

import re

def extract_mobile_numbers(text):
    # Revised pattern: allows 7 or 8 digits, captures optional trailing hyphen
    pattern = r'(?<![\d০-৯.])((?:\+?[৮8][৮8])?(?:[0০][1১১][3-9৩-৯])(?:[0-9০-৯]{2}[-]?[0-9০-৯]{6}|[0-9০-৯]{7,8})(?:-)?)(?![\d০-৯_])'
    matches = re.findall(pattern, text)
    # Filter out any accidental matches that contain internal dots/underscores (though regex tries to prevent)
    # This filter might not be strictly necessary with the improved regex but doesn't hurt.
    matches = [m for m in matches if '.' not in m and '_' not in m]
    return matches


def extract_bengali_dates(text):
    # Define character sets and month names
    bengali_digits = r'[০-৯]'
    english_digits = r'\d' # Equivalent to [0-9]

    bengali_months_list = [
        'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন',
        'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'
    ]
    english_months_full_list = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    english_months_short_list = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]

    # Create regex parts for months
    bengali_months_pattern = rf'(?:{"|".join(bengali_months_list)})'
    english_months_pattern = rf'(?:{"|".join(english_months_full_list)}|{"|".join(english_months_short_list)})'

    # --- Regex Pattern ---
    # Use re.VERBOSE for readability
    # Use non-capturing groups (?:...) where possible
    # Number backreferences correctly!
    date_pattern = rf'''
        (?<![{english_digits}{bengali_digits}]) # Lookbehind: Ensure not preceded by any digit
        ( # START Main Capturing Group (Group 1) - Captures the whole date string
            # --- Bengali Digit Formats ---
            # Format: DD Month, YYYY or DDsuffix Month YYYY (Bengali Digits)
            {bengali_digits}{{1,2}}(?:লা|ই|শে|ঠা|এ|রা)?\s+{bengali_months_pattern}(?:\s*,)?\s*{bengali_digits}{{4}}
            |
            # Format: DD/Month/YYYY or DD-Month-YYYY (Bengali Digits)
            # Group 2 captures the separator here
            {bengali_digits}{{1,2}}([/-]){bengali_months_pattern}\2{bengali_digits}{{4}}
            |
            # Format: DD/MM/YYYY or DD-MM-YYYY (Bengali Digits, same separator)
            # Group 3 captures the separator here
            {bengali_digits}{{1,2}}([/-]){bengali_digits}{{1,2}}\3{bengali_digits}{{4}}
            |
             # Format: YYYY/MM/DD or YYYY-MM-DD (Bengali Digits, same separator)
             # Group 4 captures the separator here
            {bengali_digits}{{4}}([/-]){bengali_digits}{{1,2}}\4{bengali_digits}{{1,2}}

            # --- Add English Digit Versions ---
            |
            # Format: DD Month, YYYY or DDth Month YYYY (English Digits)
             {english_digits}{{1,2}}(?:st|nd|rd|th)?\s+{english_months_pattern}(?:\s*,)?\s*{english_digits}{{4}}
            |
             # Format: DD/Month/YYYY or DD-Month-YYYY (English Digits)
             # Group 5 captures the separator here
            {english_digits}{{1,2}}([/-]){english_months_pattern}\5{english_digits}{{4}}
            |
            # Format: DD/MM/YYYY or DD-MM-YYYY (English Digits, same separator)
            # Group 6 captures the separator here
            {english_digits}{{1,2}}([/-]){english_digits}{{1,2}}\6{english_digits}{{4}}
            |
            # Format: YYYY/MM/DD or YYYY-MM-DD (English Digits, same separator)
            # Group 7 captures the separator here
            {english_digits}{{4}}([/-]){english_digits}{{1,2}}\7{english_digits}{{1,2}}
        ) # END Main Capturing Group (Group 1)

        # Lookahead: Ensure followed by a boundary (space, comma, period, Bengali daari, semicolon, end, or punctuation)
        (?=\s|,|$|।|;|[?!])
    '''

    # findall returns a list of tuples if there are capturing groups.
    # Group 1 is the main group capturing the full date string.
    # Groups 2-7 capture the separators ([/-]) in the relevant alternatives.
    # We only want the content of Group 1.
    matches = [m[0] for m in re.findall(date_pattern, text, re.VERBOSE | re.IGNORECASE)]
    return matches


def extract_distance(sentence: str) -> list[str]:
    number_pattern_str = r"[\d০-৯]+(?:\.[\d০-৯]+)?"

    units_list = [
        "km", "hm", "dam", "cm", "mm", "µm", "um", "nm", "pm", "dm",
        "mi", "fur", "ch", "yd", "ft", "in",
        "m", '\"', "\'"
    ]
    units_pattern_str = r"(?:" + "|".join(units_list) + r")"

    single_measurement_pattern = f"{number_pattern_str}{units_pattern_str}"

    dimension_separator_pattern = r"\s*[xX×]\s*"
    dimension_pattern = (
        f"{number_pattern_str}{units_pattern_str}"
        f"{dimension_separator_pattern}"
        f"{number_pattern_str}{units_pattern_str}"
    )

    regex_for_findall = f"{dimension_pattern}|{single_measurement_pattern}"

    nsw_found_list = re.findall(regex_for_findall, sentence)
    return nsw_found_list


def extract_numbers(text):
    """
    Extracts standalone numbers (integers or floats, Bengali or English digits).
    Excludes numbers that are part of other patterns like dates, times, phone numbers etc.
    ( relies on the main normalizer running this *after* other specific types).
    Handles optional commas as thousands separators.
    """
    # Pattern allows optional commas between digits, but not at the start/end.
    # It also allows a decimal point.
    pattern = r'(?<![0-9০-৯.,৳])(?:[-−]?)([0-9০-৯]+(?:,[0-9০-৯]{3})*(?:\.[0-9০-৯]+)?|[0-9০-৯]+\.[0-9০-৯]+)(?![0-9০-৯.,%])'
    # We capture the sign separately if needed, or handle it in the conversion
    matches = re.findall(pattern, text)
     # Post-filter to remove empty strings if the pattern allows optional parts that might result in empty captures
    matches = [m for m in matches if m]
    return matches

def extract_time(text):
    """
    Extracts time occurrences. Supports HH:MM, HH:MM:SS, optional AM/PM (various formats),
    optional trailing "টায়", Bengali or English digits.
    """
    # Added A.M./P.M. with dots. Made AM/PM case-insensitive.
    # Boundary checks added to prevent partial matches within words/numbers.
    pattern = r'(?<![0-9০-৯])([0-9০-৯]{1,2}:[0-9০-৯]{2}(?::[0-9০-৯]{2})?(?:\s*(?:AM|PM|A\.M\.|P\.M\.))?(?:\s*(?:টায়|মিনিটে))?)(?![0-9০-৯])'

    matches = re.findall(pattern, text, re.IGNORECASE)
    # findall captures the content of group 1 defined by the outer parentheses (...)
    return matches

def extract_taka_amounts(text):
    """
    Extracts Taka amounts. Includes ৳ symbol, words টাকা/টাকার, Bengali/English digits, commas, decimals.
    Handles cases like ৳<num> লক্ষ/কোটি specifically.
    """
    # Combined pattern with specific handling for লক্ষ/কোটি after ৳
    taka_pattern = (
        r'(?:'
        # Case 1: Starts with ৳, allows commas, decimals, optional টাকা(র)/লক্ষ/কোটি
        r'৳\s*[০-৯0-9,]+(?:\.[০-৯0-9]+)?(?:\s*(?:টাকা(?:র)?|লক্ষ|কোটি))?'
        r'|'
        # Case 2: Number followed by টাকা(র) (must have the word)
        r'(?<![৳\d০-৯.,])' # Ensure not preceded by symbol or digit
        r'[০-৯0-9,]+(?:\.[০-৯0-9]+)?\s*টাকা(?:র)?'
        r')'
         # Case 3: Specific word amounts like 'দশ লক্ষ টাকা' (handle separately if needed or rely on number + taka word)
    )

    matches = re.findall(taka_pattern, text)
     # Clean up matches that might just be the symbol or word if regex is too broad
    matches = [m.strip() for m in matches if re.search(r'[০-৯0-9]', m)]
    return matches

def extract_percentages(text):
    """ Extracts percentages with % or শতাংশ, Bengali/English digits, decimals. """
    # Added boundary checks. Allows space before % or শতাংশ.
    pattern = r'(?<![0-9০-৯.,])([-−]?[০-৯0-9,]+(?:\.[০-৯0-9]+)?)\s*(?:%|শতাংশ)(?![0-9০-৯.])'
    matches = re.findall(pattern, text)
    # Return the number part along with the symbol/word for context in normalization
    return [m + ('%' if '%' in full_match else ' শতাংশ') for m, full_match in zip(matches, re.findall(r'((?<![0-9০-৯.,])[-−]?[০-৯0-9,]+(?:\.[০-৯0-9]+)?\s*(?:%|শতাংশ)(?![0-9০-৯.]))', text))]


def extract_temperatures(text):
    """
    Extracts all temperature values from the given Bengali text and returns them as a list.

    Supported formats:
    - ৩০° সেলসিয়াস (Bengali digits with degree symbol followed by "সেলসিয়াস")
    - ৩০°C (Bengali digits with degree symbol and C)
    - ৩০ ডিগ্রি সেলসিয়াস (Bengali digits followed by "ডিগ্রি সেলসিয়াস")
    - ৩০.৫ ডিগ্রি (Bengali digits with decimal point followed by "ডিগ্রি")
    - -১০° সে. (Negative Bengali digits with degree symbol followed by abbreviated "সে.")
    - ৯৮.৬°F (Bengali digits with decimal point followed by degree symbol and F)
    - ৩০ ডিগ্রি তাপমাত্রা (Bengali digits followed by "ডিগ্রি তাপমাত্রা")

    Args:
        text (str): The text to search for temperature values

    Returns:
        list: A list of strings containing all matched temperature values
    """
    # Pattern to match temperature values in various formats
    temperature_pattern =  r'[-−]?[০-৯0-9]+(?:\.[০-৯0-9]+)?(?:\s*°(?:\s*(?:[CcFfKk]|সে\.?(?:\s*লসিয়াসে?)?)?)?|\s*ডিগ্রি(?:\s*সেলসিয়াসে?|\s*ফারেনহাইটে?)?)'

    # Find all matches
    matches = re.findall(temperature_pattern, text)

    return matches


def extract_ratios(text):
    """ Extracts ratios like X:Y, XঃY, X-Y, X থেকে Y, X অনুপাত Y. Handles numbers with decimals/commas. """
    # Pattern tries to capture common ratio formats. Handles multiple parts greedily.
    # Needs careful normalization later.
    num_pattern = r'[০-৯0-9,]+(?:\.[০-৯0-9]+)?'
    pattern = rf'''
        (?<![\d০-৯.,]) # Boundary check
        (
            {num_pattern}(?:\s*[:ঃ-]\s*{num_pattern})+  # Format X:Y:Z or X-Y-Z etc.
            |
            {num_pattern}\s*থেকে\s*{num_pattern}      # Format X থেকে Y
            |
            {num_pattern}\s*অনুপাত\s*{num_pattern}    # Format X অনুপাত Y
        )
        # Optional trailing words like অনুপাতে/রেশিওতে
        (?:\s*(?:অনুপাতে|রেশিওতে))?
        (?!\s*[:ঃ-]) # Avoid matching start of a longer ratio again
    '''
    matches = re.findall(pattern, text, re.VERBOSE)
    # Flatten list if complex groups used, keep only the main match string
    matches = [m[0] if isinstance(m, tuple) else m for m in matches]
    # Basic post-filtering for sanity
    matches = [m for m in matches if any(c in m for c in ':ঃ-') or 'থেকে' in m or 'অনুপাত' in m]
    return matches

def extract_ordinals(text):
    """
    Extracts ordinals: ১লা, ২য়, 3rd, ১০ম, 10,000তম, ১০,০০,০০০তম etc.
    Handles Bengali and English ordinals, allows commas with Bengali or English digits.
    """
    pattern = r'(?<!\S)([০-৯0-9]+(?:,[0-9০-৯]+)*(?:ম|য়|য়|লা|রা|শে|ই|র্থ|তম)|\d+(?:,\d+)*(?:st|nd|rd|th))(?=\s|[।,;:.?!]|$)'
    matches = re.findall(pattern, text)
    return matches


def extract_years_with_context(text):
    patterns = [
        r'(\d{4})\s*(সাল|সন)',  # Year directly followed by সাল or সন
        r'(সাল|সন)\s*(\d{4})',  # সাল or সন directly followed by year
        r'(\d{4})\s*(সালের|এর\s*দশকে|সাল,)'  # Year with variations of সাল
    ]

    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Extract the year from different match types
            for match in matches:
                if isinstance(match, tuple):
                    # If match is a tuple, find the year element
                    year = match[0] if len(match[0]) == 4 else match[1]
                    years.append(year)
                else:
                    years.append(match)

    return years

# --- END OF FILE exteactor.py ---