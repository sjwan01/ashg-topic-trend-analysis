from enum import Enum

class ParsingStage(Enum):
    TITLE = 'TITLE'
    AUTHORS = 'AUTHORS'
    AFFILIATIONS = 'AFFILIATIONS'
    CONTENT = 'CONTENT'