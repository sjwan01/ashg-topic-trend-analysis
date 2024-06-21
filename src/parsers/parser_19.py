from ..utils import *
import pandas as pd

def parser_19(document):
    
    data = []

    for page in document:
        current_stage = None
        blocks = page.get_text('dict')['blocks']
        lines = get_lines_from_column(blocks)
        last_line_bbox = None
        
        for line in lines:
            content = get_text(line).replace('ﬃ', 'ffi')
            current_line_bbox = line['bbox']

            if re.search(r'View Session|Add to Schedule', content):
                continue

            title_match = re.search(r'PgmNr\s*(\d+):\s*(.*)', content)
            authors_match = re.search(r'Author[s]?:\s*(.*)', content)
            affiliations_match = re.search(r'Affiliation[s]?:\s*(.*)', content)

            if title_match:
                current_stage = ParsingStage.TITLE
                data.append(dict(id=title_match.group(1), title=title_match.group(2) + ' ', authors='', affiliations='', content=''))
            elif authors_match:
                current_stage = ParsingStage.AUTHORS
                if authors_match.group(1):
                    data[-1].update(dict(authors=authors_match.group(1) + ' '))
            elif affiliations_match:
                current_stage = ParsingStage.AFFILIATIONS
                last_line_bbox = current_line_bbox
                if affiliations_match.group(1):
                    data[-1].update(dict(affiliations=affiliations_match.group(1) + ' '))

            if title_match or authors_match or affiliations_match:
                continue

            if not current_stage or last_line_bbox and abs(last_line_bbox[3] - current_line_bbox[3]) > 45:
                current_stage = ParsingStage.CONTENT

            if data:
                data = update_data(data, current_stage, content)
            
            last_line_bbox = current_line_bbox
    
    return pd.DataFrame(data).applymap(lambda x: x.rstrip())