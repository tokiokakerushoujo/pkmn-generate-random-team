import os
from src.rando_parsers.parse_randomizer_htm_log import PkmnRandomizerHtmLogParser
from src.rando_parsers.parse_randomizer_txt_log import PkmnRandomizerTextLogParser
from abc import ABC, abstractmethod


class AbstractPkmnRandoLogParser(ABC):
    def __init__(self):
        self.wild_pkmn = None
        self.pkmn_by_location = None
        self.pkmn_stats = None
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
    def from_htm(cls, htm_logfile_path: os.PathLike):
        try:
            with open(htm_logfile_path, "r", encoding="utf-8") as htmfp:
                parser = PkmnRandomizerHtmLogParser(htmfp)
                return parser
        except UnicodeDecodeError:
            try:
                with open(htm_logfile_path, "r", encoding="windows-1252") as htmfp:
                    parser = PkmnRandomizerHtmLogParser(htmfp)
                    return parser
            except: 
                raise

    @classmethod
    def from_txt(cls, logfile_path: os.PathLike):
        parser = PkmnRandomizerTextLogParser(logfile_path)
        return parser
