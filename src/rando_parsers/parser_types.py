from src.rando_parsers.parse_randomizer_htm_log import PkmnRandomizerHtmLogParser
from src.rando_parsers.parse_randomizer_txt_log import PkmnRandomizerTextLogParser
from abc import ABC, abstractmethod


class AbstractPkmnRandoLogParser(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_stats_for_pkmn(self):
        raise NotImplementedError

    @abstractmethod
    def get_locations_for_pkmn(self):
        raise NotImplementedError


AbstractPkmnRandoLogParser.register(PkmnRandomizerHtmLogParser)
AbstractPkmnRandoLogParser.register(PkmnRandomizerTextLogParser)


class PkmnRandomizerLogParser(AbstractPkmnRandoLogParser):
    def __init__(self) -> None:
        raise RuntimeError(
            "Construct this class using class method from_htm or from_log"
        )

    @classmethod
    def from_htm(cls, htm_logfile_path: str = ""):
        with open(htm_logfile_path, "r", encoding="windows-1252") as htmfp:
            parser = PkmnRandomizerHtmLogParser(htmfp)
            return parser

    @classmethod
    def from_txt(cls, logfile_path: str = ""):
        parser = PkmnRandomizerTextLogParser(logfile_path)
        return parser
