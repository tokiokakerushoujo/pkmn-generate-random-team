import random
from parse_randomizer_htm_log import PkmnRandomizerHtmLogParser
from parse_randomizer_txt_log import PkmnRandomizerTextLogParser

# should probably declare some pokemon data types to keep me honest
# pokemon are just a typed dict so it shouldnt be bad


class PkmnRandomizerLogParser:
    def __init__(self) -> None:
        raise RuntimeError(
            "Construct this class using class method from_htm or from_log"
        )

    @classmethod
    def from_htm(cls, htm_logfile_path):
        with open(htm_logfile_path, "r", encoding="windows-1252") as htmfp:
            parser = PkmnRandomizerHtmLogParser(htmfp)
            return parser

    @classmethod
    def from_txt(cls, logfile_path: str = ""):
        parser = PkmnRandomizerTextLogParser(logfile_path)
        return parser


def test():
    print("Test.")
    htm_parser:PkmnRandomizerHtmLogParser = PkmnRandomizerLogParser.from_htm("./testing/test_emerald.gba.log.html")
    txt_parser:PkmnRandomizerTextLogParser = PkmnRandomizerLogParser.from_txt("./testing/test_zx_emerald.gba.log")

    htm_testpkmn = htm_parser.get_stats_for_pkmn("AIPOM")
    txt_testpkmn = txt_parser.get_stats_for_pkmn("AIPOM")

    print(htm_testpkmn)
    print(txt_testpkmn)

    htm_testpkmn_locs = htm_parser.get_locations_for_pkmn("AIPOM")
    txt_testpkmn_locs = txt_parser.get_locations_for_pkmn("AIPOM")

    print(list(htm_testpkmn_locs))
    print(list(txt_testpkmn_locs))

if __name__ == "__main__":
    test()
