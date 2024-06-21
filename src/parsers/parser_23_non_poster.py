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
                if data and not (data[-1]['authors'] and data[-1]['content']):
                    data.pop()
                current_stage = ParsingStage.TITLE
                data.append(dict(title=title_match.group(1) + ' ', authors='', content='', header=header))
            elif authors_match:
                current_stage = ParsingStage.AUTHORS
                if authors_match.group(1):
                    data[-1].update(dict(authors=authors_match.group(1) + ' '))
            elif not current_stage or content_match:
                current_stage = ParsingStage.CONTENT
                if data and content_match and content_match.group(1):
                    data[-1].update(dict(content=content_match.group(1) + ' '))

            if topic_match or title_match or authors_match or content_match or not current_stage:
                continue

            if data:
                data = update_data(data, current_stage, content)

    return pd.DataFrame(data).applymap(lambda x: x.rstrip())