import re

def extract_mobile_numbers(text):
    """
    Extracts Bangladeshi mobile numbers from the input text.
    Handles optional country code (+88 or ৮৮), different digit lengths (7 or 8 digits),
    Bengali and English digits, and optional trailing hyphens.
    Returns a list of matched numbers after filtering out those with invalid characters.
    """
    pattern = r'(?<![\d০-৯.])((?:\+?[৮8][৮8])?(?:[0০][1১১][3-9৩-৯])(?:[0-9০-৯]{2}[-]?[0-9০-৯]{6}|[0-9০-৯]{7,8})(?:-)?)(?![\d০-৯_])'
    matches = re.findall(pattern, text)
    matches = [m for m in matches if '.' not in m and '_' not in m]
    return matches


def extract_bengali_dates(text):
    """
    Extracts dates written in Bangla or English format with various separators and styles.
    Supports formats with month names, slashes, hyphens, optional suffixes, and years.
    Returns only the matched full date strings from the input text.
    """
    bengali_digits = r'[০-৯]'
    english_digits = r'\d'

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

    bengali_months_pattern = rf'(?:{"|".join(bengali_months_list)})'
    english_months_pattern = rf'(?:{"|".join(english_months_full_list)}|{"|".join(english_months_short_list)})'

    date_pattern = rf'''
        (?<![{english_digits}{bengali_digits}])
        (
            {bengali_digits}{{1,2}}(?:লা|ই|শে|ঠা|এ|রা)?\s+{bengali_months_pattern}(?:\s*,)?\s*{bengali_digits}{{4}}
            |
            {bengali_digits}{{1,2}}([/-]){bengali_months_pattern}\2{bengali_digits}{{4}}
            |
            {bengali_digits}{{1,2}}([/-]){bengali_digits}{{1,2}}\3{bengali_digits}{{4}}
            |
            {bengali_digits}{{4}}([/-]){bengali_digits}{{1,2}}\4{bengali_digits}{{1,2}}
            |
            {english_digits}{{1,2}}(?:st|nd|rd|th)?\s+{english_months_pattern}(?:\s*,)?\s*{english_digits}{{4}}
            |
            {english_digits}{{1,2}}([/-]){english_months_pattern}\5{english_digits}{{4}}
            |
            {english_digits}{{1,2}}([/-]){english_digits}{{1,2}}\6{english_digits}{{4}}
            |
            {english_digits}{{4}}([/-]){english_digits}{{1,2}}\7{english_digits}{{1,2}}
        )
        (?=\s|,|$|।|;|[?!])
    '''
    matches = [m[0] for m in re.findall(date_pattern, text, re.VERBOSE | re.IGNORECASE)]
    return matches


def extract_numbers(text):
    """
    Extracts standalone numeric values (integers or floats) using Bengali or English digits.
    Skips those within other patterns like dates or phone numbers.
    Supports optional commas and decimal points.
    """
    pattern = r'(?<![0-9০-৯.,৳])(?:[-−]?)([0-9০-৯]+(?:,[0-9০-৯]{3})*(?:\.[0-9০-৯]+)?|[0-9০-৯]+\.[0-9০-৯]+)(?![0-9০-৯.,%])'
    matches = re.findall(pattern, text)
    matches = [m for m in matches if m]
    return matches


def extract_distance(sentence: str) -> list[str]:
    """
    Extracts Non-Standard Words (NSWs) related to distance and dimension units from Bangla or English text.

    Supports:
    - Multiple numeral systems: Arabic (0-9), Bangla (০-৯)
    - Various measurement units: m, km, cm, mm, µm, mi, ft, in, ", ', etc.
    - Dimension expressions: 12' x 10", ২০m × ১০m
    - Single units: 11", ১৫০cm, 2.5km

    Returns:
        list[str]: All matched NSW strings (e.g., ['১০ ফুট', '৫ ইঞ্চি', '২০ মিটার', '২.৫ কিলোমিটার'])
    """
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


def extract_time(text):
    """
    Extracts time expressions in HH:MM or HH:MM:SS format using Bengali or English digits.
    Also handles AM/PM formats and optional suffixes like 'টায়' or 'মিনিটে'.
    """
    pattern = r'(?<![0-9০-৯])([0-9০-৯]{1,2}:[0-9০-৯]{2}(?::[0-9০-৯]{2})?(?:\s*(?:AM|PM|A\.M\.|P\.M\.))?(?:\s*(?:টায়|মিনিটে))?)(?![0-9০-৯])'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches


def extract_taka_amounts(text):
    """
    Extracts monetary amounts in Bangladeshi Taka.
    Supports formats with the ৳ symbol, Bengali or English numerals, and words like টাকা, লক্ষ, কোটি.
    """
    taka_pattern = (
        r'(?:'
        r'৳\s*[০-৯0-9,]+(?:\.[০-৯0-9]+)?(?:\s*(?:টাকা(?:র)?|লক্ষ|কোটি))?'
        r'|'
        r'(?<![৳\d০-৯.,])'
        r'[০-৯0-9,]+(?:\.[০-৯0-9]+)?\s*টাকা(?:র)?'
        r')'
    )
    matches = re.findall(taka_pattern, text)
    matches = [m.strip() for m in matches if re.search(r'[০-৯0-9]', m)]
    return matches


def extract_percentages(text):
    """
    Extracts percentage values using % or শতাংশ with Bengali or English digits.
    Supports optional decimals and minus signs.
    """
    pattern = r'(?<![0-9০-৯.,])([-−]?[০-৯0-9,]+(?:\.[০-৯0-9]+)?)\s*(?:%|শতাংশ)(?![0-9০-৯.])'
    matches = re.findall(pattern, text)
    return [m + ('%' if '%' in full_match else ' শতাংশ') for m, full_match in zip(matches, re.findall(r'((?<![0-9০-৯.,])[-−]?[০-৯0-9,]+(?:\.[০-৯0-9]+)?\s*(?:%|শতাংশ)(?![0-9০-৯.]))', text))]


def extract_temperatures(text):
    """
    Extracts temperature values written in various Bangla or mixed formats.
    Supports degrees (°), Celsius/Fahrenheit/Kelvin indicators, and variants like "ডিগ্রি সেলসিয়াস", "F", etc.
    """
    temperature_pattern =  r'[-−]?[০-৯0-9]+(?:\.[০-৯0-9]+)?(?:\s*°(?:\s*(?:[CcFfKk]|সে\.?(?:\s*লসিয়াসে?)?)?)?|\s*ডিগ্রি(?:\s*সেলসিয়াসে?|\s*ফারেনহাইটে?)?)'
    matches = re.findall(temperature_pattern, text)
    return matches


def extract_ratios(text):
    """
    Extracts ratio expressions like X:Y, XঃY, X থেকে Y, and X অনুপাত Y.
    Supports Bengali and English digits, decimals, and optional ratio suffixes.
    """
    num_pattern = r'[০-৯0-9,]+(?:\.[০-৯0-9]+)?'
    pattern = rf'''
        (?<![\d০-৯.,])
        (
            {num_pattern}(?:\s*[:ঃ-]\s*{num_pattern})+
            |
            {num_pattern}\s*থেকে\s*{num_pattern}
            |
            {num_pattern}\s*অনুপাত\s*{num_pattern}
        )
        (?:\s*(?:অনুপাতে|রেশিওতে))?
        (?!\s*[:ঃ-])
    '''
    matches = re.findall(pattern, text, re.VERBOSE)
    matches = [m[0] if isinstance(m, tuple) else m for m in matches]
    matches = [m for m in matches if any(c in m for c in ':ঃ-') or 'থেকে' in m or 'অনুপাত' in m]
    return matches


def extract_ordinals(text):
    """
    Extracts ordinal numbers like ১লা, ২য়, ১০ম, 3rd, etc.
    Supports both Bengali and English forms with optional commas in large numbers.
    """
    pattern = r'(?<!\S)([০-৯0-9]+(?:,[0-9০-৯]+)*(?:ম|য়|য়|লা|রা|শে|ই|র্থ|তম)|\d+(?:,\d+)*(?:st|nd|rd|th))(?=\s|[।,;:.?!]|$)'
    matches = re.findall(pattern, text)
    return matches


def extract_years_with_context(text):
    """
    Extracts years with contextual words like সাল, সন, দশকে, etc.
    Handles variations where the word comes before or after the year.
    """
    patterns = [
        r'(\d{4})\s*(সাল|সন)',
        r'(সাল|সন)\s*(\d{4})',
        r'(\d{4})\s*(সালের|এর\s*দশকে|সাল,)'
    ]

    years = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    year = match[0] if len(match[0]) == 4 else match[1]
                    years.append(year)
                else:
                    years.append(match)

    return years
