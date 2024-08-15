from ..utils import *
import pandas as pd


def parser_19(document):
    """
    Parses a PDF document containing ASHG (American Society of Human Genetics) abstracts from 2019.
    The function extracts and organizes key information such as the abstract ID, title, authors, affiliations, and content.

    Parameters:
    -----------
    document : list
        A list of pages, where each page is represented as a dictionary containing blocks of text along with
        metadata such as bounding box coordinates.

    Returns:
    --------
    pd.DataFrame
        A DataFrame where each row represents an individual abstract extracted from the document with the following columns:
        - id: A unique identifier for the abstract.
        - title: The title of the abstract.
        - authors: The authors associated with the abstract.
        - affiliations: The affiliations of the authors.
        - content: The main body or content of the abstract.
    """

    data = []  # Initialize an empty list to store the parsed data

    for page in document:  # Iterate over each page in the document
        current_stage = None  # Initialize the current parsing stage
        blocks = page.get_text("dict")["blocks"]  # Extract text blocks from the page
        lines = get_lines_from_column(
            blocks
        )  # Get individual lines from the text blocks
        last_line_bbox = None  # Track the bounding box of the last processed line

        for line in lines:  # Iterate over each line in the page
            content = get_text(line).replace(
                "ﬃ", "ffi"
            )  # Extract and clean the text content
            current_line_bbox = line["bbox"]  # Get the bounding box of the current line

            # Skip lines containing session or schedule information
            if re.search(r"View Session|Add to Schedule", content):
                continue

            # Match and extract the abstract ID and title
            title_match = re.search(r"PgmNr\s*(\d+):\s*(.*)", content)
            # Match and extract the authors
            authors_match = re.search(r"Author[s]?:\s*(.*)", content)
            # Match and extract the affiliations
            affiliations_match = re.search(r"Affiliation[s]?:\s*(.*)", content)

            # If the line contains a title, start a new entry
            if title_match:
                current_stage = ParsingStage.TITLE  # Set the current stage to TITLE
                data.append(
                    dict(
                        id=title_match.group(1),  # Extract the abstract ID
                        title=title_match.group(2)
                        + " ",  # Extract the title and append a space for continuation
                        authors="",  # Initialize the authors field
                        affiliations="",  # Initialize the affiliations field
                        content="",  # Initialize the content field
                    )
                )
            # If the line contains authors, update the current entry with authors
            elif authors_match:
                current_stage = ParsingStage.AUTHORS  # Set the current stage to AUTHORS
                data[-1].update(
                    dict(authors=authors_match.group(1) + " ")
                ) if authors_match.group(
                    1
                ) else None  # Append authors to the last entry
            # If the line contains affiliations, update the current entry with affiliations
            elif affiliations_match:
                current_stage = (
                    ParsingStage.AFFILIATIONS
                )  # Set the current stage to AFFILIATIONS
                last_line_bbox = current_line_bbox  # Update the last line bounding box
                data[-1].update(
                    dict(affiliations=affiliations_match.group(1) + " ")
                ) if affiliations_match.group(
                    1
                ) else None  # Append affiliations to the last entry

            # Skip to the next line if the current one matched any of the above categories
            if title_match or authors_match or affiliations_match:
                continue

            # Determine if the current line belongs to the content section
            current_stage = (
                ParsingStage.CONTENT
                if not current_stage
                or last_line_bbox
                and is_content_start_y(last_line_bbox, current_line_bbox, 45)
                else current_stage
            )
            # Update the content field of the last entry
            data = update_data(data, current_stage, content) if data else data
            last_line_bbox = current_line_bbox  # Update the last line bounding box

    # Convert the parsed data into a DataFrame and strip trailing whitespace from each field
    return pd.DataFrame(data).astype(str).applymap(lambda x: x.rstrip())
