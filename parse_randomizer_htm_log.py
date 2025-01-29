from bs4 import BeautifulSoup
import random

class PkmnRandomizer:
    def __init__(self, randomizer_logfile) -> None:
        self.available_pkmn = None
        self.pkmn_stats = None 
        self.pkmn_locations = None        
        self.parse_html_log(randomizer_logfile) # init
    
    def find_pkmn_location_info(self):
        self.pkmn_locations = {}
        html_pk_set_lists = self.soup.find_all("ul", class_="pk-set-list")
        for pk_set_list in html_pk_set_lists:
            location = pk_set_list.find_previous("div").get_text().strip()
            pk_set_list_text = pk_set_list.get_text().strip()
            pkmn_in_pk_set = list(filter(lambda p: p != "", map(str.strip, pk_set_list_text.split('\n'))))
            self.pkmn_locations[location] = pkmn_in_pk_set

        self.available_pkmn = set()
        for pkmn_loc in self.pkmn_locations:
            for pkmn in self.pkmn_locations[pkmn_loc]:
                if (pkmn.startswith("Lv")):
                    continue
                else:
                    self.available_pkmn.add(pkmn)
        
    def find_stats_table(self):
        html_stats_table_label = self.soup.find("h2", id="ps")
        if html_stats_table_label is None:
            raise LookupError("Could not find stats table heading.")
        html_stats_table = html_stats_table_label.find_next()
        if html_stats_table is None:
            raise Exception("Something went wrong.")

        return html_stats_table

    def find_pkmn_base_stats(self):
        table_headers = ["num", "species", "type", "hp", "atk", "def", "spe", "spatk", "spdef", "total","ability1","ability2", "item", "big"]
        html_stats_table = self.find_stats_table()        
        stats_table_rows = html_stats_table.find_all("tr") #type: ignore
        for stats_row in stats_table_rows:
            if (self.pkmn_stats is None):
                self.pkmn_stats = {}
                continue
            this_pkmn = {}
            stats_cells = stats_row.find_all("td")
            for (ind, stat_cell) in enumerate(stats_cells):
                this_pkmn[table_headers[ind]] = stat_cell.get_text().strip()
            
            self.pkmn_stats[this_pkmn["species"]] = this_pkmn



    def parse_html_log(self, html_log):
        self.soup = BeautifulSoup(html_log, "html.parser")
        self.find_pkmn_location_info()
        self.find_pkmn_base_stats()

    def get_stats_for_pkmn(self, pkmn, include_locations=False, include_moves=False):
        if self.pkmn_stats is None:
            raise LookupError("Pokemon stats table not populated.")
        this_pkmn = self.pkmn_stats[pkmn]

        # mutations for human readability/convenience
        if (this_pkmn["ability1"] == "-------"):
            this_pkmn["ability1"] = this_pkmn["ability2"]
        if (this_pkmn["ability2"] == "-------"):
            this_pkmn["ability2"] = this_pkmn["ability1"]

        # single-time mutations: if called again, avoid doing them
        if "num" in this_pkmn:
            del this_pkmn["num"]
        if "big" in this_pkmn:
            del this_pkmn["big"]
        if isinstance(this_pkmn["type"], str):
            this_pkmn["type"] = this_pkmn["type"].split("\n")
        if isinstance(this_pkmn["item"], str):
            this_pkmn["item"] = list(map(str.strip, this_pkmn["item"].split('\n')))

        # passed param-based inclusions -- dont include if flag not passed, so delete it
        if (include_locations):
            this_pkmn["locations"] = list(self.get_locations_for_pkmn(pkmn))
        elif "locations" in this_pkmn:
            del this_pkmn["locations"]

        if (include_moves):
            this_pkmn["moves"] = []
        elif "moves" in this_pkmn:
            del this_pkmn["moves"]
        
        return this_pkmn
        
    def get_locations_for_pkmn(self, pkmn):
        if self.pkmn_locations is None:
            raise LookupError("Pokemon stats table not populated.")
        for loc in self.pkmn_locations:
            if (pkmn in self.pkmn_locations[loc]):
                yield loc
    
    def get_nfe_list(self):
        NFE_LIST = []
        with open("./lists/nfe.txt", "r") as nfe_file:
            NFE_LIST = nfe_file.readlines()
        return NFE_LIST

    def get_random_team_from_available_pokemon(self, force_fully_evolved=False):
        if self.available_pkmn is None:
            raise LookupError("Pokemon availability table not populated.")

        pkmn = random.sample(list(self.available_pkmn), 6)
        # add section for filter to non-NFEs?
        if (force_fully_evolved):
            NFE_LIST = self.get_nfe_list()  
            for (ind, pk) in enumerate(pkmn):
                new_pkmn = pk
                while new_pkmn in NFE_LIST and new_pkmn not in pkmn:
                    new_pkmn = random.choice(list(self.available_pkmn))
                pkmn[ind] = new_pkmn
        
        team = []
        for member in pkmn:
            team.append(self.get_stats_for_pkmn(member, include_locations=True))
        return team

    def choose_encounter_for_all_locations(self):
        if self.pkmn_locations is None:
            raise LookupError("Pokemon stats table not populated.")
        location_encounters = {}
        for loc in self.pkmn_locations:
            locations = filter(lambda p: not p.startswith("Lv"), self.pkmn_locations[loc])
            encounter = random.choice(list(set(locations)))
            location_encounters[loc] = self.get_stats_for_pkmn(encounter)
        
        return location_encounters


if __name__ == "__main__":
    infile = "test_emerald.gba.log.html"
    with open(infile, "r", encoding="windows-1252") as fp:
        pkr = PkmnRandomizer(fp)
        # print(pkr.get_random_team_from_available_pokemon())
        print(pkr.choose_encounter_for_all_locations())