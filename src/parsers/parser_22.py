from ..utils import *
import pandas as pd


def parser_22(document):
    """
    Parses a PDF document containing ASHG (American Society of Human Genetics) abstracts from 2022.
    The function extracts and organizes key information such as the abstract ID, title, authors, content, and headers.

    Parameters:
    -----------
    document : list
        A list where each element represents a page in the PDF document. Each page contains blocks of text
        with associated metadata such as bounding box coordinates.

    Returns:
    --------
    pd.DataFrame
        A DataFrame where each row represents an individual abstract extracted from the document with the following columns:
        - id: A unique identifier for the abstract.
        - title: The title of the abstract.
        - authors: The authors associated with the abstract.
        - content: The main body or content of the abstract.
        - header: The topic or session header associated with the abstract.
    """

    data = []  # Initialize an empty list to store the parsed data

    for page in document:  # Iterate over each page in the document
        current_stage = None  # Initialize the current parsing stage
        blocks = page.get_text("dict")["blocks"]  # Extract text blocks from the page
        lines = get_lines_from_column(
            blocks
        )  # Get individual lines from the text blocks

        for line in lines:  # Iterate over each line in the page
            content = get_text(line)  # Extract the text content of the line

            # Skip lines that contain certain metadata or session information
            if re.search(
                r"ASHG 2022 Annual Meeting .+ Abstracts|Page\s+(\d+)\s+of\s+(\d+)|^(Location|Session Time)",
                content,
            ):
                continue

            # Match and extract the session or topic header
            topic_match = re.search(
                r"S\d{2}\.\s*(.+)|(.+) Posters\s*-\s*(?:Wednesday|Thursday)", content
            )
            # Match and extract the abstract ID and title
            title_match = re.search(r"(?:ProgNbr|PB)\s*(\d+)\*?[:.]\s*(.+)", content)
            # Match and extract the authors
            authors_match = re.search(r"Authors:\s*(.*)", content)
            # Match and extract the abstract content
            content_match = re.search(r"Abstract(?: Body)?:\s*(.*)", content)

            # If the line contains a topic or session header, start a new entry
            if topic_match:
                data.append(
                    dict(
                        id="",  # Initialize the ID field
                        title="",  # Initialize the title field
                        authors="",  # Initialize the authors field
                        content="",  # Initialize the content field
                        header=topic_match.group(1)
                        or topic_match.group(2),  # Extract the header
                    )
                )
            # If the line contains a title, update the current entry with the ID and title
            elif data and title_match:
                current_stage = ParsingStage.TITLE  # Set the current stage to TITLE
                data[-1].update(
                    dict(
                        id=title_match.group(1),  # Extract the abstract ID
                        title=title_match.group(2)
                        + " ",  # Extract the title and append a space for continuation
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
            # If the line contains content, update the current entry with content
            elif not current_stage or content_match:
                current_stage = ParsingStage.CONTENT  # Set the current stage to CONTENT
                data[-1].update(
                    dict(content=content_match.group(1) + " ")
                ) if content_match and content_match.group(
                    1
                ) else None  # Append content to the last entry

            # Skip to the next line if the current one matched any of the above categories
            if (
                topic_match
                or title_match
                or authors_match
                or content_match
                or not current_stage
            ):
                continue

            # Update the content field of the last entry with any remaining text
            data = update_data(data, current_stage, content) if data else data

    # Convert the parsed data into a DataFrame and strip trailing whitespace from each field
    return pd.DataFrame(data).astype(str).applymap(lambda x: x.rstrip())
