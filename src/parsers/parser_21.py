from ..utils import *
import pandas as pd

def parser_21(document):

    def partial_parser(pages):

        data = []

        for page in pages:
            current_stage = None
            blocks = page.get_text('dict')['blocks']
            lines = get_lines_from_column(blocks)

            for line in lines:
                content = get_text(line)

                if line['spans'][0]['size'] == 8 or re.search('View session detail', content):
                    continue

                title_match = re.search(r'PrgmNr\s*(\d+)\s*-\s*(.*)', content)
                authors_match = re.search(r'Author Block:\s*(.*)', content)
                content_match = re.search(r'Disclosure Block:\s*(.*)', content)

                if title_match:
                    current_stage = ParsingStage.TITLE
                    data.append(dict(id=title_match.group(1), title=title_match.group(2) + ' ', authors='', content=''))
                elif authors_match:
                    current_stage = ParsingStage.AUTHORS
                    data[-1].update(dict(authors=authors_match.group(1) + ' '))
                elif not current_stage or content_match:
                    current_stage = ParsingStage.CONTENT
                    data[-1].update(dict(content=content_match.group(1) + ' ')) if content_match else None

                if title_match or authors_match or content_match or not current_stage:
                    continue

                data = update_data(data, current_stage, content) if data else data

        return pd.DataFrame(data).applymap(lambda x: x.rstrip())

    for pages in [range(73, 89), range(90, 295), range(296, 379), range(380, 2224)]:
        yield partial_parser(map(document.__getitem__, pages))