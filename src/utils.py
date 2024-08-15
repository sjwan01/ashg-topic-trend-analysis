import re
import requests
import os
import logging
from bs4 import BeautifulSoup
from .enums import ParsingStage

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def ensure_folder_exists(folder_path):
    """
    Ensures that a folder exists at the specified path. If the folder does not exist, it will be created.

    Parameters:
    -----------
    folder_path : str
        The path to the folder that needs to be checked or created.

    Returns:
    --------
    None
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logging.info(f"Created folder: {folder_path}")
    else:
        logging.info(f"Folder already exists: {folder_path}")


def fetch_and_parse_url(url):
    """
    Fetches the content of the specified URL and parses it using BeautifulSoup.

    Parameters:
    -----------
    url : str
        The URL to fetch and parse.

    Returns:
    --------
    BeautifulSoup
        A BeautifulSoup object containing the parsed HTML content if the request is successful.
        Returns None if there is an error fetching the URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None


def download_file(link, folder_path):
    """
    Downloads a file from the given URL and saves it to the specified folder. If the
    file already exists, it will not be downloaded again.

    Parameters:
    -----------
    link : str
        The URL of the file to be downloaded.
    folder_path : str
        The path to the folder where the file should be saved.

    Returns:
    --------
    None
    """
    filename = os.path.join(folder_path, link.split("/")[-1])
    if os.path.exists(filename):
        logging.info(f"{filename} already exists in {folder_path}")
        return
    try:
        file_response = requests.get(link)
        file_response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(file_response.content)
        logging.info(f"Successfully downloaded {filename}")
    except requests.RequestException as e:
        logging.error(f"Error downloading {link}: {e}")


def get_lines_from_column(blocks):
    """
    Extracts and rebuilds lines of text from a list of text blocks, considering their bounding box coordinates.

    Parameters:
    -----------
    blocks : list
        A list of blocks, where each block contains lines of text with associated metadata (bounding box and spans).

    Returns:
    --------
    list of dict
        A list of lines, each represented as a dictionary containing 'spans' and 'bbox'.
    """
    lines = []
    for block in blocks:
        if "image" not in block:
            for line in block["lines"]:
                if not skip(line):
                    lines.append(dict(spans=line["spans"], bbox=line["bbox"]))

    rebuilt_lines = []
    for line in lines:
        if not rebuilt_lines or abs(line["bbox"][1] - rebuilt_lines[-1]["bbox"][1]) > 5:
            for idx, span in enumerate(line["spans"]):
                if span["text"].strip():
                    rebuilt_lines.append(
                        dict(spans=line["spans"][idx:], bbox=list(line["bbox"]))
                    )
                    rebuilt_lines[-1]["bbox"][0] = line["spans"][idx]["bbox"][0]
                    break
        else:
            rebuilt_lines[-1]["spans"].extend(line["spans"])
            rebuilt_lines[-1]["bbox"][2] = line["bbox"][2]

    return rebuilt_lines


def get_lines_from_page(page):
    """
    Extracts and organizes text lines from a page into left and right columns and identifies the topic of the page.

    Parameters:
    -----------
    page : object
        A page object containing text blocks with metadata.

    Returns:
    --------
    tuple
        A tuple where the first element is a list of organized lines (from left and right columns) and the second element is the topic of the page.
    """
    page_dict = page.get_text("dict")
    mid = page_dict["width"] / 2
    left_blocks, right_blocks, topic = [], [], ""

    for block in page_dict["blocks"]:
        if "lines" not in block:
            continue

        content = " ".join(get_text(line) for line in block["lines"])
        if block["bbox"][2] < mid + 20:
            left_blocks.append(block)
        elif block["bbox"][0] > mid - 20:
            right_blocks.append(block)
        elif not re.search("Copyright", content):
            topic = re.sub(r"\s*Posters:?\s*|\s*\d+\s*", "", content).strip()

    left_lines, right_lines = map(get_lines_from_column, [left_blocks, right_blocks])
    return left_lines + right_lines, topic


def update_data(data, current_stage, content):
    """
    Updates the current entry in the data list based on the current parsing stage and the content.

    Parameters:
    -----------
    data : list of dict
        The list of parsed data entries.
    current_stage : ParsingStage
        The current stage of parsing (e.g., TITLE, AUTHORS, CONTENT).
    content : str
        The content to be added to the current stage of the data entry.

    Returns:
    --------
    list of dict
        The updated list of parsed data entries.
    """
    match current_stage:
        case ParsingStage.TITLE:
            data[-1]["title"] = (
                data[-1]["title"].rstrip()
                if ends_with_dash(data[-1]["title"])
                else data[-1]["title"]
            )
            data[-1]["title"] += content + " "
        case ParsingStage.AUTHORS:
            data[-1]["authors"] += content + " "
        case ParsingStage.AFFILIATIONS:
            data[-1]["affiliations"] += content + " "
        case ParsingStage.CONTENT:
            data[-1]["content"] = (
                data[-1]["content"].rstrip()
                if ends_with_dash(data[-1]["content"])
                else data[-1]["content"]
            )
            data[-1]["content"] += content + " "

    return data


def is_id(line):
    """
    Checks if a line represents an identifier based on font size.

    Parameters:
    -----------
    line : dict
        A dictionary representing a line with metadata.

    Returns:
    --------
    bool
        True if the line's font size indicates it is an identifier, otherwise False.
    """
    return line["spans"][0]["size"] == 10


def is_page_num(line):
    """
    Checks if a line represents a page number based on font size and content.

    Parameters:
    -----------
    line : dict
        A dictionary representing a line with metadata.

    Returns:
    --------
    bool
        True if the line represents a page number, otherwise False.
    """
    return line["spans"][0]["size"] == 9 and get_text(line).strip().isdigit()


def is_marker(line):
    """
    Checks if a line contains a specific marker text.

    Parameters:
    -----------
    line : dict
        A dictionary representing a line with metadata.

    Returns:
    --------
    bool
        True if the line contains the marker text, otherwise False.
    """
    return "Trainee Award Finalist" in get_text(line)


def get_text(line):
    """
    Extracts and concatenates text from a line, handling special characters.

    Parameters:
    -----------
    line : dict
        A dictionary representing a line with text spans.

    Returns:
    --------
    str
        The concatenated text from the line.
    """
    return " ".join(
        span["text"].replace("\x00", " ") for span in line["spans"]
    ).rstrip()


def is_empty(line):
    """
    Checks if a line is empty based on its text content.

    Parameters:
    -----------
    line : dict
        A dictionary representing a line with text spans.

    Returns:
    --------
    bool
        True if the line is empty, otherwise False.
    """
    return not get_text(line)


def skip(line):
    """
    Determines whether a line should be skipped based on its content.

    Parameters:
    -----------
    line : dict
        A dictionary representing a line with metadata.

    Returns:
    --------
    bool
        True if the line should be skipped, otherwise False.
    """
    return is_page_num(line) or is_marker(line)


def ends_with_dash(string):
    """
    Checks if a string ends with a dash character.

    Parameters:
    -----------
    string : str
        The string to check.

    Returns:
    --------
    bool
        True if the string ends with a dash, otherwise False.
    """
    return string.rstrip().endswith("-")


def get_fonts_and_texts(line):
    """
    Extracts fonts and text segments from a line, handling special characters.

    Parameters:
    -----------
    line : dict
        A dictionary representing a line with text spans.

    Returns:
    --------
    tuple
        A tuple containing two lists:
        - fonts: A list of fonts used in the line.
        - texts: A list of text segments.
    """
    if line:
        fonts, texts = [], []
        for span in line["spans"]:
            font = span["font"]
            text = span["text"]
            if "\x00" in text:
                split_texts = text.split("\x00")
                split_texts = [t for t in split_texts if t]
                texts.extend(split_texts)
                fonts.extend([font] * len(split_texts))
            else:
                texts.append(text)
                fonts.append(font)
        return fonts, texts
    return [], []


def get_last_bold_font_index(fonts):
    """
    Finds the index of the last bold font in a list of fonts.

    Parameters:
    -----------
    fonts : list
        A list of font names.

    Returns:
    --------
    int
        The index of the last bold font, or -1 if none are found.
    """
    last_bold_idx = -1
    for idx, font in enumerate(fonts):
        last_bold_idx = idx if "Bold" in font else last_bold_idx
    return last_bold_idx


def is_title_end(string):
    """
    Checks if a string ends with a punctuation mark typically used to end a title.

    Parameters:
    -----------
    string : str
        The string to check.

    Returns:
    --------
    bool
        True if the string ends with a period, exclamation mark, or question mark, otherwise False.
    """
    return string.rstrip().endswith((".", "!", "?"))


def is_authors_end(string):
    """
    Checks if a string ends with a period, indicating the end of the authors section.

    Parameters:
    -----------
    string : str
        The string to check.

    Returns:
    --------
    bool
        True if the string ends with a period, otherwise False.
    """
    return string.rstrip().endswith(".")


def is_content_start_x1(line, x1):
    """
    Checks if the content in a line starts a new section based on its horizontal position and text content.

    Parameters:
    -----------
    line : dict
        A dictionary representing a line with bounding box metadata.
    x1 : float
        The x-coordinate used to determine if the content starts a new section.

    Returns:
    --------
    bool
        True if the line starts a new content section, otherwise False.
    """
    return (
        abs(line["bbox"][0] - x1) > 5 or get_text(line).startswith(("\xa0", " "))
        if line
        else False
    )


def is_content_start_x2(line, x2):
    """
    Checks if the content in a line starts a new section based on its horizontal ending position.

    Parameters:
    -----------
    line : dict
        A dictionary representing a line with bounding box metadata.
    x2 : float
        The x2-coordinate used to determine if the content starts a new section.

    Returns:
    --------
    bool
        True if the line starts a new content section, otherwise False.
    """
    return abs(line["bbox"][2] - x2) > 20 if line else False


def is_content_start_y(last_line_bbox, current_line_bbox, threshold):
    """
    Checks if the content in a line starts a new section based on its vertical position.

    Parameters:
    -----------
    last_line_bbox : list
        The bounding box coordinates of the previous line.
    current_line_bbox : list
        The bounding box coordinates of the current line.
    threshold : float
        The vertical distance threshold used to determine if content starts a new section.

    Returns:
    --------
    bool
        True if the content starts a new section based on the vertical position, otherwise False.
    """
    return abs(last_line_bbox[3] - current_line_bbox[3]) > threshold
