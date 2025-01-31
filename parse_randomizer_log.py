import random
from parse_randomizer_htm_log import PkmnRandomizerHtmLogParser
from parse_randomizer_txt_log import PkmnRandomizerNormalLogParser

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
    def from_log(cls, logfile_path: str = ""):
        parser = PkmnRandomizerNormalLogParser(logfile_path)
        return parser


def test():
    print("Test.")
    infile = "test_zx_emerald.gba.log"
    pkr = PkmnRandomizerLogParser.from_log(logfile_path=infile)
    team = random.sample(list(pkr.wild_pokemon), 6)
    for member in team:
        print(member, pkr.get_pokemon_stats(member))


if __name__ == "__main__":
    test()
