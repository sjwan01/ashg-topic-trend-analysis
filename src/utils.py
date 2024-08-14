import re
from .enums import ParsingStage

def get_lines_from_column(blocks):
    lines = []
    for block in blocks:
        if 'image' not in block:
            for line in block['lines']:
                lines.append(dict(spans=line['spans'], bbox=line['bbox'])) if not skip(line) else None
    rebuilt_lines = []
    for line in lines:
        if not rebuilt_lines or abs(line['bbox'][1] - rebuilt_lines[-1]['bbox'][1]) > 5:
            for idx, span in enumerate(line['spans']):
                if span['text'].strip():
                    rebuilt_lines.append(dict(spans=line['spans'][idx:], bbox=list(line['bbox'])))
                    rebuilt_lines[-1]['bbox'][0] = line['spans'][idx]['bbox'][0]
                    break
        else:
            rebuilt_lines[-1]['spans'].extend(line['spans'])
            rebuilt_lines[-1]['bbox'][2] = line['bbox'][2]
    return rebuilt_lines

def get_lines_from_page(page):
    page_dict = page.get_text('dict')
    mid = page_dict['width'] / 2
    left_blocks, right_blocks, topic = [], [], ''
    for block in page_dict['blocks']:
        if 'lines' not in block:
            continue
        content = ' '.join(get_text(line) for line in block['lines'])
        if block['bbox'][2] < mid + 20:
            left_blocks.append(block)
        elif block['bbox'][0] > mid - 20:
            right_blocks.append(block)
        elif not re.search('Copyright', content):
            topic = re.sub(r'\s*Posters:?\s*|\s*\d+\s*', '', content).strip()
    left_lines, right_lines = map(get_lines_from_column, [left_blocks, right_blocks])
    return left_lines + right_lines, topic

def update_data(data, current_stage, content):
    match current_stage:
        case ParsingStage.TITLE:
            data[-1]['title'] = data[-1]['title'].rstrip() if ends_with_dash(data[-1]['title']) else data[-1]['title']
            data[-1]['title'] += content + ' '
        case ParsingStage.AUTHORS:
            data[-1]['authors'] += content + ' '
        case ParsingStage.AFFILIATIONS:
            data[-1]['affiliations'] += content + ' '
        case ParsingStage.CONTENT:
            data[-1]['content'] = data[-1]['content'].rstrip() if ends_with_dash(data[-1]['content']) else data[-1]['content']
            data[-1]['content'] += content + ' '
    return data

def is_id(line):
    return line['spans'][0]['size'] == 10

def is_page_num(line):
    return line['spans'][0]['size'] == 9 and get_text(line).strip().isdigit()

def is_marker(line):
    return 'Trainee Award Finalist' in get_text(line)

def get_text(line):
    return ' '.join(span['text'].replace('\x00', ' ') for span in line['spans']).rstrip()

def is_empty(line):
    return not get_text(line)

def skip(line):
    return is_page_num(line) or is_marker(line)

def ends_with_dash(string):
    return string.rstrip().endswith('-')

def get_fonts_and_texts(line):
    if line:
        fonts, texts = [], []
        for span in line['spans']:
            font = span['font']
            text = span['text']
            if '\x00' in text:
                split_texts = text.split('\x00')
                split_texts = [t for t in split_texts if t]
                texts.extend(split_texts)
                fonts.extend([font] * len(split_texts))
            else:
                texts.append(text)
                fonts.append(font)
        return fonts, texts
    return [], []

def get_last_bold_font_index(fonts):
    last_bold_idx = -1
    for idx, font in enumerate(fonts):
        last_bold_idx = idx if 'Bold' in font else last_bold_idx
    return last_bold_idx

def is_title_end(string):
    return string.rstrip().endswith(('.', '!', '?'))

def is_authors_end(string):
    return string.rstrip().endswith('.')

def is_content_start_x1(line, x1):
    return abs(line['bbox'][0] - x1) > 5 or get_text(line).startswith(('\xa0', ' ')) if line else False

def is_content_start_x2(line, x2):
    return abs(line['bbox'][2] - x2) > 20 if line else False

def is_content_start_y(last_line_bbox, current_line_bbox, threshold):
    return abs(last_line_bbox[3] - current_line_bbox[3]) > threshold