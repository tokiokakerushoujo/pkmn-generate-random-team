from typing import Optional, TypedDict, cast
from bs4 import BeautifulSoup

# for use with the Brentspector release of the universal pkmn randomizer apparently.
# if your rando has "version 1.10.3" somewhere in it, you're gonna get an HTML log
from src.rando_parsers.pkmn_types import PkmnStatBlock

class PkmnRandomizerHtmLogParser:
    def __init__(self, logfile) -> None:
        # [azurill, lotad, vulpix, ...]
        self.wild_pkmn = set()
        # { "Set #1 - ROUTE 101 Grass/Cave (rate=20)": { azurill: { level_floor: 2, level_ceil: 3 }}, lotad: { ... } }
        self.pkmn_by_location = None
        # { azurill: num: 289, hp: 66, atk: 25, def_: 41, spatk: 33, spdef: 11, spe: 15, ability1: SAND VEIL, ability2: SAND VEIL, items: None, types: [PSYCHIC, DRAGON], ...}
        self.pkmn_stats: dict[str, PkmnStatBlock]|None = None
        self.parse_html_log(logfile)  # init

    def find_wild_pkmn_location_info(self):
        self.pkmn_by_location = {}
        self.wild_pkmn = set()
        html_pk_set_lists = self.soup.find_all("ul", class_="pk-set-list")
        for pk_set_list in html_pk_set_lists:
            location = pk_set_list.find_previous("div").get_text().strip()
            pk_set_list_text = pk_set_list.get_text().strip()
            pkmn_in_pk_set = list(
                filter(lambda p: p != "", map(str.strip, pk_set_list_text.split("\n")))
            )

            for pkmn in pkmn_in_pk_set[0::2]:
                self.wild_pkmn.add(pkmn)

            pk_tuples = zip(pkmn_in_pk_set[0::2], pkmn_in_pk_set[1::2])
            level_ranges = self.generate_location_level_ranges(pk_tuples)
            self.pkmn_by_location[location] = level_ranges


    def generate_location_level_ranges(self, loc_tuples):
        pkmn_data = {}
        for (species, lvrng) in loc_tuples:
            if species in pkmn_data:
                level_floor = pkmn_data[species]["level_floor"]
                level_ceil = pkmn_data[species]["level_ceil"]
            else:
                level_floor = 101
                level_ceil = 0
            
            if len(lvrng.split('-')) < 2:
                # aka "Lv 50".split('-') => ['Lv 50']
                new_lvl_floor = new_lvl_ceil = int(lvrng[3:])
            else:
                # "Lvs 50-60" => ["lvs 50", "60"]
                [new_lvl_floor, new_lvl_ceil] = map(int, lvrng[4:].split(' - '))
            
            pkmn_data[species] = {
                "level_floor": min(new_lvl_floor, level_floor),
                "level_ceil": max(new_lvl_ceil, level_ceil)
            }

        return pkmn_data

    def find_stats_table(self):
        html_stats_table_label = self.soup.find("h2", id="ps")
        if html_stats_table_label is None:
            raise LookupError("Could not find stats table heading.")
        html_stats_table = html_stats_table_label.find_next()
        if html_stats_table is None:
            raise Exception("Something went wrong.")

        return html_stats_table

    def find_pkmn_base_stats(self):
        table_headers = [
            "num",
            "species",
            "type",
            "hp",
            "atk",
            "def",
            "spe",
            "spatk",
            "spdef",
            "total",
            "ability1",
            "ability2",
            "item",
            "big",
        ]
        html_stats_table = self.find_stats_table()
        stats_table_rows = html_stats_table.find_all("tr")  # type: ignore
        for stats_row in stats_table_rows:
            if self.pkmn_stats is None:
                self.pkmn_stats = {}
                continue
            this_pkmn = {}
            stats_cells = stats_row.find_all("td")
            for ind, stat_cell in enumerate(stats_cells):
                this_pkmn[table_headers[ind]] = stat_cell.get_text().strip()

            self.pkmn_stats[this_pkmn["species"]] = self.format_pkmn_stat_block(this_pkmn)

    def parse_html_log(self, html_log):
        self.soup = BeautifulSoup(html_log, "html.parser")
        self.find_wild_pkmn_location_info()
        self.find_pkmn_base_stats()

    def format_pkmn_stat_block(self, this_pkmn):
        # mutations for human readability/convenience
        if this_pkmn["ability1"] == "-------":
            this_pkmn["ability1"] = this_pkmn["ability2"]
        if this_pkmn["ability2"] == "-------":
            this_pkmn["ability2"] = this_pkmn["ability1"]

        # single-time mutations: if called again, avoid doing them
        if "num" in this_pkmn:
            del this_pkmn["num"]
        if "big" in this_pkmn:
            del this_pkmn["big"]
        if "item" in this_pkmn:
            this_pkmn["items"] = list(map(str.strip, this_pkmn["item"].split("\n")))
            del this_pkmn["item"]
        if "type" in this_pkmn:
            this_pkmn["types"] = this_pkmn["type"].split("\n")
            del this_pkmn["type"]
        if "total" in this_pkmn:
            this_pkmn["total"] = int(this_pkmn["total"])

        stat_names = ["hp", "spe", "atk", "spatk", "def", "spdef"]
        for stat_name in stat_names:
            this_pkmn[stat_name] = int(this_pkmn[stat_name])


        # passed param-based inclusions -- dont include if flag not passed, so delete it
        this_pkmn["locations"] = list(self.get_locations_for_pkmn(this_pkmn["species"]))

        return cast(PkmnStatBlock, this_pkmn)

    def get_stats_for_pkmn(self, species: str) -> PkmnStatBlock:
        """Retrieve the parsed data for a given Pokemon species by name.

        Args:
            species (str): The name of the pokemon.

        Raises:
            LookupError: If the pokemon data has not been loaded or the pokemon does not exist in that data.

        Returns:
            PkmnStatBlock: The statblock of the randomized pokemon. 
        """
        if self.pkmn_stats is None:
            raise LookupError("Pokemon stats table not populated.")
        
        this_pkmn = self.pkmn_stats[species]
        return this_pkmn

    def get_locations_for_pkmn(self, pkmn):
        if self.pkmn_by_location is None:
            raise LookupError("Pokemon stats table not populated.")
        for loc in self.pkmn_by_location:
            if pkmn in self.pkmn_by_location[loc]:
                yield loc