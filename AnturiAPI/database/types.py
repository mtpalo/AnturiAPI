
from enum import Enum

class TilaTyyppi(str, Enum):
    NORMAALI = 'NORMAALI'
    VIRHE = 'VIRHE'

class MittausTyyppi(str, Enum):
    TEMP = 'LÄMPÖTILA'