import os
from typing import Optional, cast
from src.rando_parsers.pkmn_types import PkmnStatBlock
import re


class PkmnRandomizerTextLogParser:
    # notes to self:
    # 1. generate a proper docstring later
    # 2:
    # - find_* methods search the input file for their thing and set some internal value
    # - get_* methods retrieve from internal values and return their values

    def __init__(self, logfile: os.PathLike) -> None:
        self.log_data = self.read_log(logfile)
        # [azurill, lotad, vulpix, ...]
        self.wild_pkmn = set()
        # { "Set #1 - ROUTE 101 Grass/Cave (rate=20)": { azurill: { level_floor: 2, level_ceil: 3 }}, lotad: { ... } }
        self.pkmn_by_location = None
        # { azurill: num: 289, hp: 66, atk: 25, def_: 41, spatk: 33, spdef: 11, spe: 15, ability1: SAND VEIL, ability2: SAND VEIL, items: None, types: [PSYCHIC, DRAGON], ...}
        self.pkmn_stats: dict[str, PkmnStatBlock]|None = None

        # init
        self.find_wild_pkmn_location_info()
        self.find_pkmn_base_stats()

    def read_log(self, logfile: os.PathLike):
        with open(logfile, "r", encoding="utf-8") as log:
            log_data = log.readlines()
            return log_data

    def is_wild_set_declaration(self, line: str):
        wild_set_match = re.match(r"^(Set \#\d*\s+.*)", line)
        return wild_set_match is not None

    def find_wild_set_lines(self):
        return [
            ind
            for (ind, line) in enumerate(self.log_data)
            if self.is_wild_set_declaration(line)
        ]

    def find_wild_pkmn_info_in_range(
        self, start_line_index: int, end_line_index: Optional[int] = None
    ):
        wild_set_pkmn_regex = re.compile(
            r"^(?P<species>.*)(?=\s+Lv)\s+Lv((?P<lv>\d+)|s\s+(?P<lvrng>\d+\-\d+))", re.I
        )
        curr_ind = start_line_index + 1
        curr_match = wild_set_pkmn_regex.match(self.log_data[curr_ind])
        while curr_match is not None and (
            end_line_index is None
            or (end_line_index is not None and curr_ind < end_line_index)
        ):
            yield curr_match.groupdict()
            curr_ind += 1
            curr_match = wild_set_pkmn_regex.match(self.log_data[curr_ind])

    def generate_location_level_ranges(self, wild_pkmn_data: list[dict]):
        pkmn_data = {}
        for wild_pkmn in wild_pkmn_data:
            if (pkmn := wild_pkmn["species"]) in pkmn_data:
                level_floor = pkmn_data[pkmn]["level_floor"]
                level_ceil = pkmn_data[pkmn]["level_ceil"]
            else:
                level_floor = 101
                level_ceil = 0

            if "lvrng" in wild_pkmn and wild_pkmn["lvrng"] is not None:
                # "25-36" => ["25", "36"] => [25,36] = [floor, ceil]
                [new_lvl_floor, new_lvl_ceil] = map(int, wild_pkmn["lvrng"].split("-"))
            elif "lv" in wild_pkmn and wild_pkmn["lv"] is not None:
                new_lvl_floor = new_lvl_ceil = int(wild_pkmn["lv"])

            level_ceil = max(level_ceil, new_lvl_ceil)
            level_floor = min(level_floor, new_lvl_floor)

            pkmn_data[pkmn] = {"level_floor": level_floor, "level_ceil": level_ceil}
            # side-effect: this is just to make processing the list of wild pokemon easier later
            self.wild_pkmn.add(pkmn)

        return pkmn_data

    def find_wild_pkmn_location_info(self):
        if self.pkmn_by_location is None:
            self.pkmn_by_location = {}
        else:
            return self.pkmn_by_location
        # find all indexes of wild set declaration lines
        wild_set_declarations = self.find_wild_set_lines()
        # all the non-blank lines between them must be pokemon
        for wild_set_ind, wild_set_logstart_ind in enumerate(wild_set_declarations):
            wildset = self.log_data[wild_set_logstart_ind].strip()
            if wild_set_ind == len(wild_set_declarations) - 1:
                end_logindex = None
            else:
                end_logindex = wild_set_declarations[wild_set_ind + 1]
            wild_pkmn_in_set = list(
                self.find_wild_pkmn_info_in_range(wild_set_logstart_ind, end_logindex)
            )
            self.pkmn_by_location[wildset] = self.generate_location_level_ranges(
                wild_pkmn_in_set
            )

        return self.pkmn_by_location

    def format_pokemon_stats(self, regex_match) -> PkmnStatBlock:
        curr_pkmn_stats = regex_match.groupdict()
        # there can be whitespace bc of the way i captured the ability groups
        curr_pkmn_stats["ability1"] = curr_pkmn_stats["ability1"].strip()
        curr_pkmn_stats["ability2"] = curr_pkmn_stats["ability2"].strip()
        curr_pkmn_stats["species"] = curr_pkmn_stats["species"].strip()

        curr_pkmn_species = curr_pkmn_stats["species"]
        if curr_pkmn_stats["ability1"] == "-------":
            curr_pkmn_stats["ability1"] = curr_pkmn_stats["ability2"]
        if curr_pkmn_stats["ability2"] == "-------":
            curr_pkmn_stats["ability2"] = curr_pkmn_stats["ability1"]

        # checks for safety but can be omitted
        if "num" in curr_pkmn_stats:
            del curr_pkmn_stats["num"]

        if isinstance(curr_pkmn_stats["types"], str):
            curr_pkmn_stats["types"] = curr_pkmn_stats["types"].split("/")
        if isinstance(curr_pkmn_stats["items"], str):
            curr_pkmn_stats["items"] = list(
                map(str.strip, curr_pkmn_stats["items"].split(","))
            )

        if "total" not in curr_pkmn_stats:
            curr_pkmn_stats["total"] = 0

        stat_names = ["hp", "spe", "atk", "spatk", "def", "spdef"]
        for stat_name in stat_names:
            curr_pkmn_stats[stat_name] = int(curr_pkmn_stats[stat_name])
            curr_pkmn_stats["total"] += curr_pkmn_stats[stat_name]

        # passed param-based inclusions -- dont include if flag not passed, so delete it
        curr_pkmn_stats["locations"] = list(
            self.get_locations_for_pkmn(curr_pkmn_species)
        )

        return cast(PkmnStatBlock, curr_pkmn_stats)

    def find_pkmn_base_stats(self) -> dict[str, PkmnStatBlock]:
        if self.pkmn_stats is None:
            self.pkmn_stats = {}
        else:
            return self.pkmn_stats

        pkmn_stats_table_header = "--Pokemon Base Stats & Types--\n"
        # header line and then the table column definition lines are ignored
        stats_table_index = self.log_data.index(pkmn_stats_table_header) + 2
        stats_table_regex = re.compile(
            r"^\s*(?P<num>\d+)\|(?P<species>[^\|]+)\s*\|(?P<types>[^\|\s]+)\s*\|\s*(?P<hp>\d+)\|\s*(?P<atk>\d+)\|\s*(?P<def>\d+)\|\s*(?P<spatk>\d+)\|\s*(?P<spdef>\d+)\|\s*(?P<spe>\d+)\|(?P<ability1>[^\|]+)\|(?P<ability2>[^\|]+)\|(?P<items>[^\n]*)?$",
            re.I,
        )
        while (
            stats_match := stats_table_regex.match(self.log_data[stats_table_index])
        ) is not None:
            stats_table_index += 1
            curr_pkmn_stats = self.format_pokemon_stats(stats_match)
            self.pkmn_stats[curr_pkmn_stats["species"]] = curr_pkmn_stats

        return self.pkmn_stats

    def get_locations_for_pkmn(self, species):
        if self.pkmn_by_location is None:
            raise LookupError(
                f"Wild pokemon location not found, cannot locate {species} in wild pokemon list."
            )

        for location in self.pkmn_by_location:
            if species in self.pkmn_by_location[location]:
                yield location

    def get_stats_for_pkmn(self, species):
        if self.pkmn_stats is None or species not in self.pkmn_stats:
            raise LookupError(
                f"Pokemon stats not found, cannot locate {species} in pokemon stat list."
            )
        return self.pkmn_stats[species]
