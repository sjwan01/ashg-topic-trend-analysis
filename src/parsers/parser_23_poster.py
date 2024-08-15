from ..utils import *
import pandas as pd


def parser_23_poster(document):
    """
    Parses a PDF document containing ASHG (American Society of Human Genetics) 2023 poster session abstracts.
    The function extracts and organizes key information such as the abstract ID, title, authors, content, and session headers.

    Parameters:
    -----------
    document : list
        A list where each element represents a page in the PDF document. Each page contains blocks of text
        with associated metadata such as bounding box coordinates.

    Returns:
    --------
    pd.DataFrame
        A DataFrame where each row represents an individual abstract extracted from the document with the following columns:
        - id: The unique identifier for the poster.
        - title: The title of the abstract.
        - authors: The authors associated with the abstract.
        - content: The main body or content of the abstract.
        - header: The session header or topic associated with the abstract.
    """

    data = []  # Initialize an empty list to store the parsed data
    last_line_bbox = None  # Initialize the bounding box of the last processed line

    for page in document:  # Iterate over each page in the document
        current_stage = None  # Initialize the current parsing stage
        blocks = page.get_text("dict")["blocks"]  # Extract text blocks from the page
        lines = get_lines_from_column(
            blocks
        )  # Get individual lines from the text blocks

        for line in lines:  # Iterate over each line in the page
            content = get_text(line)  # Extract the text content of the line
            current_line_bbox = line[
                "bbox"
            ]  # Get the bounding box for the current line

            # Skip lines that contain metadata or page numbers
            if re.search(
                r"ASHG 2023 Annual Meeting .+ Abstracts|Page\s+(\d+)\s+of\s+(\d+)",
                content,
            ):
                continue

            # Match and extract the session or topic header for posters
            topic_match = re.search(
                r"Session Title:\s*(.+)\s*Poster Session\.*", content
            )
            # Match and extract the poster ID and title
            title_match = re.search(r"PB\s*(\d{4})\s*†?\s*(.+)", content)
            # Match and extract the authors associated with the poster
            authors_match = re.search(r"Authors:\s*(.*)", content)

            # If the line contains a topic or session header, start a new entry with the header
            if topic_match:
                data.append(
                    dict(
                        id="",
                        title="",
                        authors="",
                        content="",
                        header=topic_match.group(1),
                    )
                )
            # If the line contains a title, update the last entry with the ID and title
            elif data and title_match:
                current_stage = ParsingStage.TITLE  # Set the current stage to TITLE
                data[-1].update(
                    dict(id=title_match.group(1), title=title_match.group(2) + " ")
                )
            # If the line contains authors, update the current entry with the authors
            elif authors_match:
                current_stage = ParsingStage.AUTHORS  # Set the current stage to AUTHORS
                data[-1].update(
                    dict(authors=authors_match.group(1) + " ")
                ) if authors_match.group(1) else None

            # Skip to the next line if the current one matched any of the above categories
            if topic_match or title_match or authors_match:
                continue

            # Determine if the current line should be considered part of the content
            current_stage = (
                ParsingStage.CONTENT
                if not current_stage
                or data
                and data[-1]["authors"]
                and is_content_start_y(last_line_bbox, current_line_bbox, 20)
                else current_stage
            )
            # Update the content field of the last entry with any remaining text
            data = update_data(data, current_stage, content) if data else data
            last_line_bbox = current_line_bbox  # Update the last line's bounding box for the next iteration

    # Convert the parsed data into a DataFrame and strip trailing whitespace from each field
    return pd.DataFrame(data).astype(str).applymap(lambda x: x.rstrip())
