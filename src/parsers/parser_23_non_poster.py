from ..utils import *
import pandas as pd


def parser_23_non_poster(document):
    """
    Parses a PDF document containing ASHG (American Society of Human Genetics) platform and plenary session abstracts from 2023.
    The function extracts and organizes key information such as the abstract title, authors, content, and session headers.

    Parameters:
    -----------
    document : list
        A list where each element represents a page in the PDF document. Each page contains blocks of text
        with associated metadata such as bounding box coordinates.

    Returns:
    --------
    pd.DataFrame
        A DataFrame where each row represents an individual abstract extracted from the document with the following columns:
        - title: The title of the abstract.
        - authors: The authors associated with the abstract.
        - content: The main body or content of the abstract.
        - header: The session header or topic associated with the abstract.
    """

    data = []  # Initialize an empty list to store the parsed data
    header = ""  # Initialize the header for each session or topic

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
                r"ASHG 2023 Annual Meeting .+ Abstracts|^(Location|Session Time)",
                content,
            ):
                continue

            # Match and extract the session or topic header
            topic_match = re.search(r"Session \d{3}:\s*(.+)", content)
            # Match and extract the title of the abstract
            title_match = re.search(r"Title:\s*(.+)", content)
            # Match and extract the authors
            authors_match = re.search(r"Authors:\s*(.*)", content)
            # Match and extract the abstract content
            content_match = re.search(r"Abstract(?: Body)?:\s*(.*)", content)

            # If the line contains a topic or session header, update the current header
            if topic_match:
                header = topic_match.group(1)
            # If the line contains a title, start a new entry
            elif title_match:
                # If the last entry does not have both authors and content, remove it (incomplete entry)
                data.pop() if data and not (
                    data[-1]["authors"] and data[-1]["content"]
                ) else None
                current_stage = ParsingStage.TITLE  # Set the current stage to TITLE
                data.append(
                    dict(
                        title=title_match.group(1)
                        + " ",  # Extract the title and append a space for continuation
                        authors="",  # Initialize the authors field
                        content="",  # Initialize the content field
                        header=header,  # Use the current session header
                    )
                )
            # If the line contains authors, update the current entry with authors
            elif authors_match:
                current_stage = ParsingStage.AUTHORS  # Set the current stage to AUTHORS
                data[-1].update(
                    dict(authors=authors_match.group(1) + " ")
                ) if authors_match.group(1) else None
            # If the line contains content, update the current entry with content
            elif not current_stage or content_match:
                current_stage = ParsingStage.CONTENT  # Set the current stage to CONTENT
                data[-1].update(
                    dict(content=content_match.group(1) + " ")
                ) if content_match and content_match.group(1) else None

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
