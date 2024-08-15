from ..utils import *
import pandas as pd


def parser_21(document):
    """
    Parses a PDF document containing ASHG (American Society of Human Genetics) abstracts from 2021.
    The function extracts and organizes key information such as the abstract ID, title, authors, and content.

    The parsing process is divided into four chunks, and the function yields DataFrames for each chunk.

    Parameters:
    -----------
    document : list
        A list where each element represents a page in the PDF document. Each page contains blocks of text
        with associated metadata such as bounding box coordinates.

    Yields:
    -------
    pd.DataFrame
        A DataFrame for each range of pages processed. Each row represents an individual abstract extracted
        from the document with the following columns:
        - id: A unique identifier for the abstract.
        - title: The title of the abstract.
        - authors: The authors associated with the abstract.
        - content: The main body or content of the abstract.
    """

    def partial_parser(pages):
        """
        Processes a subset of pages from the document and extracts structured information (ID, title, authors, content).

        Parameters:
        -----------
        pages : iterable
            A sequence of pages to be processed.

        Returns:
        --------
        pd.DataFrame
            A DataFrame where each row represents an individual abstract extracted from the subset of pages with columns:
            - id: A unique identifier for the abstract.
            - title: The title of the abstract.
            - authors: The authors associated with the abstract.
            - content: The main body or content of the abstract.
        """

        data = []  # Initialize an empty list to store the parsed data

        for page in pages:  # Iterate over each page in the provided subset
            current_stage = None  # Initialize the current parsing stage
            blocks = page.get_text("dict")[
                "blocks"
            ]  # Extract text blocks from the page
            lines = get_lines_from_column(
                blocks
            )  # Get individual lines from the text blocks

            for line in lines:  # Iterate over each line in the page
                content = get_text(line)  # Extract the text content of the line

                # Skip lines with specific font size or session details
                if line["spans"][0]["size"] == 8 or re.search(
                    "View session detail", content
                ):
                    continue

                # Match and extract the abstract ID and title
                title_match = re.search(r"PrgmNr\s*(\d+)\s*-\s*(.*)", content)
                # Match and extract the authors
                authors_match = re.search(r"Author Block:\s*(.*)", content)
                # Match and extract the content block
                content_match = re.search(r"Disclosure Block:\s*(.*)", content)

                # If the line contains a title, start a new entry
                if title_match:
                    current_stage = ParsingStage.TITLE  # Set the current stage to TITLE
                    data.append(
                        dict(
                            id=title_match.group(1),  # Extract the abstract ID
                            title=title_match.group(2)
                            + " ",  # Extract the title and append a space for continuation
                            authors="",  # Initialize the authors field
                            content="",  # Initialize the content field
                        )
                    )
                # If the line contains authors, update the current entry with authors
                elif authors_match:
                    current_stage = (
                        ParsingStage.AUTHORS
                    )  # Set the current stage to AUTHORS
                    data[-1].update(
                        dict(authors=authors_match.group(1) + " ")
                    )  # Append authors to the last entry
                # If the line contains content, update the current entry with content
                elif not current_stage or content_match:
                    current_stage = (
                        ParsingStage.CONTENT
                    )  # Set the current stage to CONTENT
                    data[-1].update(
                        dict(content=content_match.group(1) + " ")
                    ) if content_match else None  # Append content to the last entry

                # Skip to the next line if the current one matched any of the above categories
                if title_match or authors_match or content_match or not current_stage:
                    continue

                # Update the content field of the last entry
                data = update_data(data, current_stage, content) if data else data

        # Convert the parsed data into a DataFrame and strip trailing whitespace from each field
        return pd.DataFrame(data).astype(str).applymap(lambda x: x.rstrip())

    # Define the ranges of pages to process in chunks and yield the result of partial parsing for each chunk
    # The chunks correspond to different sections of the ASHG 2021 abstracts:
    #   -- Plenary Sessions: pages 73-89
    #   -- Platform Sessions: pages 90-295
    #   -- Poster Talks: pages 296-379
    #   -- Poster Presentations: pages 380-2225
    for pages in [range(73, 89), range(90, 295), range(296, 379), range(380, 2224)]:
        yield partial_parser(map(document.__getitem__, pages))
