from ..utils import *
import pandas as pd

def parser_22(document):

    data = []

    for page in document:
        current_stage = None
        blocks = page.get_text('dict')['blocks']
        lines = get_lines_from_column(blocks)

        for line in lines:
            content = get_text(line)

            if re.search(r'ASHG 2022 Annual Meeting .+ Abstracts|Page\s+(\d+)\s+of\s+(\d+)|^(Location|Session Time)', content):
                continue

            topic_match = re.search(r'S\d{2}\.\s*(.+)|(.+) Posters\s*-\s*(?:Wednesday|Thursday)', content)
            title_match = re.search(r'(?:ProgNbr|PB)\s*(\d+)\*?[:.]\s*(.+)', content)
            authors_match = re.search(r'Authors:\s*(.*)', content)
            content_match = re.search(r'Abstract(?: Body)?:\s*(.*)', content)

            if topic_match:
                data.append(dict(id='', title='', authors='', content='', header=topic_match.group(1) or topic_match.group(2)))
            elif data and title_match:
                current_stage = ParsingStage.TITLE
                data[-1].update(dict(id=title_match.group(1), title=title_match.group(2) + ' '))
            elif authors_match:
                current_stage = ParsingStage.AUTHORS
                data[-1].update(dict(authors=authors_match.group(1) + ' ')) if authors_match.group(1) else None
            elif not current_stage or content_match:
                current_stage = ParsingStage.CONTENT
                data[-1].update(dict(content=content_match.group(1) + ' ')) if content_match and content_match.group(1) else None

            if topic_match or title_match or authors_match or content_match or not current_stage:
                continue

            data = update_data(data, current_stage, content) if data else data

    return pd.DataFrame(data).applymap(lambda x: x.rstrip())