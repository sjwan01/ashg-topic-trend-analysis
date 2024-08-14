from ..utils import *
import pandas as pd

def parser_23_non_poster(document):

    data = []
    header = ''

    for page in document:
        current_stage = None
        blocks = page.get_text('dict')['blocks']
        lines = get_lines_from_column(blocks)

        for line in lines:
            content = get_text(line)

            if re.search(r'ASHG 2023 Annual Meeting .+ Abstracts|^(Location|Session Time)', content):
                continue

            topic_match = re.search(r'Session \d{3}:\s*(.+)', content)
            title_match = re.search(r'Title:\s*(.+)', content)
            authors_match = re.search(r'Authors:\s*(.*)', content)
            content_match = re.search(r'Abstract(?: Body)?:\s*(.*)', content)

            if topic_match:
                header = topic_match.group(1)
            elif title_match:
                data.pop() if data and not (data[-1]['authors'] and data[-1]['content']) else None
                current_stage = ParsingStage.TITLE
                data.append(dict(title=title_match.group(1) + ' ', authors='', content='', header=header))
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