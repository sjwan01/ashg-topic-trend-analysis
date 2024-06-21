from ..utils import *
import pandas as pd

def parser_13_to_18(document):

    data = []

    for page in document:
        current_stage, x1 = None, float('inf')
        abstract_lines, topic = get_lines_from_page(page)

        for line_idx in range(len(abstract_lines)):

            line = abstract_lines[line_idx]
            x2 = line['bbox'][2]
            content = get_text(line)
            fonts, texts = get_fonts_and_texts(line)
            next_line = abstract_lines[line_idx+1] if line_idx + 1 < len(abstract_lines) else None

            if not current_stage and data:
                if not is_title_end(data[-1]['title']):
                    current_stage = ParsingStage.TITLE
                elif not is_authors_end(data[-1]['authors']):
                    current_stage = ParsingStage.AUTHORS
                else:
                    current_stage = ParsingStage.CONTENT

            if is_id(line) or content in ['2258W', '2549W', '3174T']:
                current_stage = ParsingStage.TITLE
                data.append(dict(id=content, title='', authors='', content='', header=topic))
                x1 = line['bbox'][0]
                continue

            match current_stage:
                case ParsingStage.TITLE:
                    last_bold_idx = get_last_bold_font_index(fonts)
                    next_line_fonts, _ = get_fonts_and_texts(next_line)
                    data[-1]['title'] = data[-1]['title'].rstrip()[:-1] if ends_with_dash(data[-1]['title']) else data[-1]['title']
                    if get_last_bold_font_index(next_line_fonts) != -1:
                        data[-1]['title'] += ' '.join(text for text in texts if text != data[-1]['id']).lstrip() + ' '
                    else:
                        data[-1]['title'] += ' '.join(text for text in texts[:last_bold_idx+1] if text != data[-1]['id']).lstrip()
                        data[-1]['authors'] += ' '.join(text for text in texts[last_bold_idx+1:]).lstrip() + ' '
                        current_stage = ParsingStage.CONTENT if is_content_start_x1(next_line, x1) and is_authors_end(data[-1]['authors']) else ParsingStage.AUTHORS
                case ParsingStage.AUTHORS:
                    data[-1]['authors'] = data[-1]['authors'].rstrip()[:-1] if ends_with_dash(data[-1]['authors']) else data[-1]['authors']
                    data[-1]['authors'] += (content + ' ').lstrip()
                    if (is_content_start_x1(next_line, x1) or is_content_start_x2(next_line, x2)) and is_authors_end(data[-1]['authors']):
                        current_stage = ParsingStage.CONTENT     
                case ParsingStage.CONTENT:
                    data[-1]['content'] = data[-1]['content'].rstrip()[:-1] if ends_with_dash(data[-1]['content']) else data[-1]['content']
                    data[-1]['content'] += (content + ' ').lstrip()

    return pd.DataFrame(data).applymap(lambda x: x.rstrip())