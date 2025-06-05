from .methods import *
from .extractor import *
import re
from .conversion_data import bangla_conjuncts_to_ipa, bangla_to_ipa
from .utils import translate_english_word, remove_extra_spaces, remove_punctuation



def normalize_dates(text):
    matches = extract_bengali_dates(text)
    matches = sorted(list(set(matches)), key=len, reverse=True)
    for match in matches:
        normalized_date = date_to_word(match)
        if normalized_date != match:
            text = text.replace(match, normalized_date)
    return text


def normalize_distance(text):
    matches = extract_distance(text)
    matches = sorted(list(set(matches)), key=len, reverse=True)
    for match in matches:
        normalized_distance = distance_to_word(match)
        if normalized_distance != match:
            text = text.replace(match, normalized_distance)
    return text


def normalize_phonenumbers(text):
    mobile_numbers = extract_mobile_numbers(text)
    mobile_numbers = sorted(list(set(mobile_numbers)), key=len, reverse=True)
    for number in mobile_numbers:
        normalized = phone_number_to_word(number)
        if normalized != number:
            text = text.replace(number, normalized)
    return text


def normalize_numbers(text):
    numbers = extract_numbers(text)
    numbers = sorted(list(set(numbers)), key=len, reverse=True)
    for number in numbers:
        normalized = number_to_word(number)
        text = text.replace(number, normalized)
    return text


def normalize_time(text):
    times = extract_time(text)
    times = sorted(list(set(times)), key=len, reverse=True)
    for t in times:
        normalized = time_to_word(t, text)
        if normalized != t:
            text = text.replace(t, normalized)
    return text


def normalize_taka(text):
    takas = extract_taka_amounts(text)
    takas = sorted(list(set(takas)), key=len, reverse=True)
    for taka in takas:
        normalized = taka_to_word(taka)
        if normalized != taka:
            text = text.replace(taka, normalized)
    return text


def normalize_percentage(text):
    percentages = extract_percentages(text)
    percentages = sorted(list(set(percentages)), key=len, reverse=True)
    for percentage in percentages:
        normalized = percentage_to_word(percentage)
        if normalized != percentage:
            text = text.replace(percentage, normalized)
    return text


def normalize_temperatures(text):
    temperatures = extract_temperatures(text)
    temperatures = sorted(list(set(temperatures)), key=len, reverse=True)
    for temperature in temperatures:
        normalized = temperature_to_word(temperature)
        if normalized != temperature:
            text = text.replace(temperature, normalized)
    return text


def normalize_ratio(text):
    ratios = extract_ratios(text)
    ratios = sorted(list(set(ratios)), key=len, reverse=True)
    for ratio_match in ratios:
        normalize_val = ratio_match.replace('ঃ', ' এ ')
        normalize_val = normalize_val.replace(':', ' এ ')
        normalize_val = normalize_val.replace('-', ' ')
        normalize_val = normalize_numbers(normalize_val)
        text = text.replace(ratio_match, normalize_val)
    return text


def normalize_ordinal(text):
    words = extract_ordinals(text)
    words = sorted(list(set(words)), key=len, reverse=True)
    for word in words:
        normalized = ordinal_to_word(word)
        if normalized != word:
            text = text.replace(word, normalized)
    return text


def normalize_year(text):
    words = extract_years_with_context(text)
    words = sorted(list(set(words)), key=len, reverse=True)
    for word in words:
        normalized = year_to_word(word)
        if normalized != word :
             text = text.replace(word, normalized)
    return text


def split_into_sentences(text):
    """
    Split Bangla `text` into individual sentences while preserving end
    punctuation marks.
    """
    pattern = r'([^।?!]+[।?!]?)'
    sentences = re.findall(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def join_sentences(sentences):
    """
    Join a list of sentences into a single string, separating them with a
    space.
    """
    return ' '.join(sentences)


def normalize_text(text):
    """
    Run the full normalisation pipeline on `text`.  For inputs longer than
    `THRESHOLD`, the text is processed sentence-by-sentence; any segment that
    fails to normalise is left unchanged.
    """
    THRESHOLD = 150

    normalization_pipeline = [
        normalize_distance,
        normalize_temperatures,
        normalize_time,
        normalize_dates,
        normalize_phonenumbers,
        normalize_taka,
        normalize_percentage,
        normalize_ratio,
        normalize_ordinal,
        normalize_year,
        normalize_numbers,
        translate_english_word,
        remove_extra_spaces,
    ]

    def process_chunk(chunk):
        """
        Apply every function in `normalization_pipeline` to `chunk`
        sequentially.
        """
        processed = chunk
        for normalizer in normalization_pipeline:
            processed = normalizer(processed)
        return processed

    if len(text) <= THRESHOLD:
        try:
            return process_chunk(text)
        except Exception as e:
            print(f'Error normalizing text: {e}\nReturning original text.')
            return text

    sentences = split_into_sentences(text)
    normalized_sentences = []

    for sentence in sentences:
        try:
            normalized_sentence = process_chunk(sentence)
        except Exception as e:
            print(
                f"Error processing sentence: '{sentence}'\nError: {e}\nLeaving sentence as-is."
            )
            normalized_sentence = sentence
        normalized_sentences.append(normalized_sentence)

    return join_sentences(normalized_sentences)


def bangla_to_ipa_converter(sentence):
    """
    Convert a Bangla sentence to its IPA (International Phonetic Alphabet)
    representation using both conjunct and character mappings from
    `conversion_data.py`. Unmapped characters are passed through unchanged.
    """
    sentence = remove_punctuation(sentence)
    sentence = normalize_text(sentence)
    ipa_output = ""
    i = 0
    max_conj_length = max(len(key) for key in bangla_conjuncts_to_ipa) if bangla_conjuncts_to_ipa else 0
    while i < len(sentence):
        match_found = False
        for l in range(max_conj_length, 0, -1):
            if i + l <= len(sentence):
                segment = sentence[i:i + l]
                if segment in bangla_conjuncts_to_ipa:
                    ipa_output += bangla_conjuncts_to_ipa[segment]
                    i += l
                    match_found = True
                    break
        if not match_found:
            char = sentence[i]
            ipa_output += bangla_to_ipa.get(char, char)
            i += 1
    return ipa_output