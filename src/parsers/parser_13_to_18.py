from ..utils import *
import pandas as pd


def parser_13_to_18(document):
    """
    Parses a PDF document containing ASHG (American Society of Human Genetics) abstracts from the years 2013 to 2018.
    The function extracts and organizes key information such as the abstract ID, title, authors, and content.

    Parameters:
    -----------
    document : list
        A list of pages, where each page is represented as a dictionary containing lines of text along with
        metadata such as bounding box coordinates and font details.

    Returns:
    --------
    pd.DataFrame
        A DataFrame where each row represents an individual abstract extracted from the document with the following columns:
        - id: A unique identifier for the abstract.
        - title: The title of the abstract.
        - authors: The authors associated with the abstract.
        - content: The main body or content of the abstract.
        - header: The header or topic associated with the abstract, typically indicating the session or section.
    """

    data = []  # List to store the parsed data from the document

    for page in document:  # Iterate over each page in the document
        current_stage, x1 = None, float(
            "inf"
        )  # Initialize parsing stage and x1 coordinate
        abstract_lines, topic = get_lines_from_page(
            page
        )  # Extract lines and topic from the page

        for line_idx in range(
            len(abstract_lines)
        ):  # Iterate over each line in the page
            line = abstract_lines[line_idx]
            x2 = line["bbox"][2]  # Get the x2 coordinate of the line's bounding box
            content = get_text(line)  # Extract the text content of the line
            fonts, texts = get_fonts_and_texts(
                line
            )  # Extract fonts and text segments from the line
            next_line = (
                abstract_lines[line_idx + 1]
                if line_idx + 1 < len(abstract_lines)
                else None
            )  # Get the next line if it exists

            # Determine the current parsing stage based on the last processed data
            if not current_stage and data:
                if not is_title_end(data[-1]["title"]):
                    current_stage = ParsingStage.TITLE
                elif not is_authors_end(data[-1]["authors"]):
                    current_stage = ParsingStage.AUTHORS
                else:
                    current_stage = ParsingStage.CONTENT

            # Check if the current line represents a new entry ID (elements in the list are edge cases cannot be detected as IDs)
            if is_id(line) or content in ["2258W", "2549W", "3174T"]:
                current_stage = (
                    ParsingStage.TITLE
                )  # Start a new entry, beginning with the title
                data.append(
                    dict(id=content, title="", authors="", content="", header=topic)
                )  # Initialize a new entry
                x1 = line["bbox"][0]  # Update x1 coordinate for the new entry
                continue

            # Process the line based on the current parsing stage
            match current_stage:
                case ParsingStage.TITLE:
                    last_bold_idx = get_last_bold_font_index(
                        fonts
                    )  # Identify the last bold font index
                    next_line_fonts, _ = get_fonts_and_texts(
                        next_line
                    )  # Get fonts of the next line

                    # Handle cases where the title continues on the next line
                    data[-1]["title"] = (
                        data[-1]["title"].rstrip()[:-1]
                        if ends_with_dash(data[-1]["title"])
                        else data[-1]["title"]
                    )

                    if get_last_bold_font_index(
                        next_line_fonts
                    ) != -1 and not is_content_start_x1(next_line, x1):
                        data[-1]["title"] += (
                            " ".join(
                                text for text in texts if text != data[-1]["id"]
                            ).lstrip()
                            + " "
                        )
                    else:
                        data[-1]["title"] += " ".join(
                            text
                            for text in texts[: last_bold_idx + 1]
                            if text != data[-1]["id"]
                        ).lstrip()
                        data[-1]["authors"] += (
                            " ".join(
                                text for text in texts[last_bold_idx + 1 :]
                            ).lstrip()
                            + " "
                        )
                        # Transition to content parsing if title and authors are complete
                        current_stage = (
                            ParsingStage.CONTENT
                            if is_content_start_x1(next_line, x1)
                            and is_authors_end(data[-1]["authors"])
                            else ParsingStage.AUTHORS
                        )

                case ParsingStage.AUTHORS:
                    # Handle cases where the authors' names continue on the next line
                    data[-1]["authors"] = (
                        data[-1]["authors"].rstrip()[:-1]
                        if ends_with_dash(data[-1]["authors"])
                        else data[-1]["authors"]
                    )
                    data[-1]["authors"] += (content + " ").lstrip()
                    # Transition to content parsing if authors section is complete
                    current_stage = (
                        ParsingStage.CONTENT
                        if (
                            is_content_start_x1(next_line, x1)
                            or is_content_start_x2(next_line, x2)
                        )
                        and is_authors_end(data[-1]["authors"])
                        else current_stage
                    )

                case ParsingStage.CONTENT:
                    # Handle cases where the content continues on the next line
                    data[-1]["content"] = (
                        data[-1]["content"].rstrip()[:-1]
                        if ends_with_dash(data[-1]["content"])
                        else data[-1]["content"]
                    )
                    data[-1]["content"] += (content + " ").lstrip()

    # Convert the parsed data into a DataFrame and strip trailing whitespace from each field
    return pd.DataFrame(data).astype(str).applymap(lambda x: x.rstrip())
