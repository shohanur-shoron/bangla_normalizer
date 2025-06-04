# --- START OF FILE normalizer.py ---

from methods import *
from exteactor import *
import re # Import re here as well

# Ensure conversion_data is loaded or accessible if methods need it directly
# from conversion_data import * # Might not be needed here if methods imports it

def normalize_dates(text):
    # Use extractor to find date strings
    matches = extract_bengali_dates(text)
    # Sort by length descending to replace longest matches first
    matches = sorted(list(set(matches)), key=len, reverse=True) # Use set to avoid duplicate processing
    for match in matches:
        normalized_date = date_to_word(match)
        if normalized_date != match: # Replace only if conversion was successful
            text = text.replace(match, normalized_date)
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
    ratios = sorted(ratios, key=len, reverse=True)
    for ratio in ratios:
        normalize = ratio.replace('ঃ', ' এ ')
        normalize = normalize.replace(':', ' এ ')
        normalize = normalize.replace('-', " ")
        normalize = normalize_numbers(normalize)
        text = text.replace(ratio, normalize)

    return text


def normalize_ordinal(text):
    words = extract_ordinals(text)
    words = sorted(list(set(words)), key=len, reverse=True)
    for word in words:
        # Use the dedicated function which handles maps and complex cases
        normalized = ordinal_to_word(word)
        if normalized != word:
            text = text.replace(word, normalized)
        # Handle simple map cases if ordinal_to_word doesn't cover them all
        # elif word in ordinal_normalization_map:
        #     text = text.replace(word, ordinal_normalization_map[word])

    return text

def normalize_year(text):
    words = extract_years_with_context(text)
    words = sorted(words, key=len, reverse=True)
    for word in words:
        normalized = year_to_word(word)
        text = text.replace(word, normalized)

    return text


def split_into_sentences(text):
    # Bangla sentences often end with "।" or can also end with question or exclamation marks.
    # This regex splits the text and preserves the punctuation.
    pattern = r'([^।?!]+[।?!]?)'
    sentences = re.findall(pattern, text)
    # Remove any empty strings from the list
    return [s.strip() for s in sentences if s.strip()]


def join_sentences(sentences):
    # Rejoin sentences with a space. Adjust if needed for proper spacing in Bangla.
    return " ".join(sentences)


def normalize_text(text):
    """
    Normalize the text by processing it in chunks if it exceeds a certain length.
    If normalization of any segment fails, that segment is left unchanged.
    """
    # Threshold can be adjusted based on what you consider "big text"
    THRESHOLD = 150  # for example, 200 characters

    # Define the normalization pipeline
    normalization_pipeline = [
        normalize_temperatures,  # Handles C/F, negative signs
        normalize_time,  # Handles AM/PM, colons
        normalize_dates,  # Handles slashes, month names
        normalize_phonenumbers,  # Handles +, hyphens, specific lengths
        normalize_taka,  # Handles ৳, টাকা, লক্ষ, কোটি
        normalize_percentage,  # Handles %, শতাংশ
        normalize_ratio,  # Handles :, -, থেকে, অনুপাত
        normalize_ordinal,  # Handles st, nd, rd, th, ম, লা etc.
        normalize_year,  # Handles সাল, সন context
        normalize_numbers,  # General number conversion (integers, floats) - LAST
        translate_english_word,
        remove_extra_spaces  # Final cleanup
    ]

    def process_chunk(chunk):
        """Apply the normalization pipeline to a single text chunk."""
        processed = chunk
        for normalizer in normalization_pipeline:
            processed = normalizer(processed)
        return processed

    # If the text is short, process it directly.
    if len(text) <= THRESHOLD:
        try:
            return process_chunk(text)
        except Exception as e:
            # Log the error if needed and return the original text.
            print(f"Error normalizing text: {e}\nReturning original text.")
            return text

    # For longer text, split it into sentences/chunks.
    sentences = split_into_sentences(text)
    normalized_sentences = []

    for sentence in sentences:
        try:
            normalized_sentence = process_chunk(sentence)
        except Exception as e:
            # On error, keep the sentence unchanged.
            print(f"Error processing sentence: '{sentence}'\nError: {e}\nLeaving sentence as-is.")
            normalized_sentence = sentence
        normalized_sentences.append(normalized_sentence)

    return join_sentences(normalized_sentences)
