from ..utils import *
import pandas as pd

def parser_23_poster(document):

    data = []

    for page in document:
        current_stage = None
        blocks = page.get_text('dict')['blocks']
        lines = get_lines_from_column(blocks)
        last_line_bbox = None

        for line in lines:
            content = get_text(line)
            current_line_bbox = line['bbox']

            if re.search(r'ASHG 2023 Annual Meeting .+ Abstracts|Page\s+(\d+)\s+of\s+(\d+)', content):
                continue

            topic_match = re.search(r'Session Title:\s*(.+)\s*Poster Session\.*', content)
            title_match = re.search(r'PB\s*(\d{4})\s*†?\s*(.+)', content)
            authors_match = re.search(r'Authors:\s*(.*)', content)

            if topic_match:
                data.append(dict(id='', title='', authors='', content='', header=topic_match.group(1)))
            elif data and title_match:
                current_stage = ParsingStage.TITLE
                data[-1].update(dict(id=title_match.group(1), title=title_match.group(2) + ' '))
            elif authors_match:
                current_stage = ParsingStage.AUTHORS
                data[-1].update(dict(authors=authors_match.group(1) + ' ')) if authors_match.group(1) else None

            if topic_match or title_match or authors_match:
                continue

            current_stage = ParsingStage.CONTENT if not current_stage or data and data[-1]['authors'] and is_content_start_y(last_line_bbox, current_line_bbox, 20) else current_stage
            data = update_data(data, current_stage, content) if data else data
            last_line_bbox = current_line_bbox

    return pd.DataFrame(data).applymap(lambda x: x.rstrip())