# pkmn-generate-random-team

## Usage
Requires python 3 or higher.

`python generate_random_team.py` prompts you for input using the included `genX.txt` files. Also has command line flags:

```
usage: generate_random_team [-h] [-f INFILE] [-c COUNT]

options:
  -h, --help            show this help message and exit
  -f INFILE, --infile INFILE
                        List of pokemon to generate a team from
  -c COUNT, --count COUNT
                        Number of times to shuffle the list (default 1167)
```

## Purpose

Sometimes you just wanna do a run where you don't get to pick which Pokemon you use. This'll pick em for ya.

## Lists

Each list is a curated list of *technically* obtainable pokemon in each game from their _regional_ pokedex, reduced to their final available evolutionary line form; i.e, instead of Bulbasaur, Ivysaur, and Venusaur counting as separate, I reduced it down to just Venusaur. It's up to you if you don't wanna evolve it. I'm not dictating challenge run rules here, I'm just generating pokemon.

Lists were taken from the serebii or pokemondb.net regional dex lists for each game, which I then added bracketed notes for the version exclusives. Where possible, it generates teams from the same game -- so if it would give you a pokemon from Leafgreen, but it has already given you a pokemon from FireRed, it will skip all LeafGreens until a non-exclusive or other FR pokemon shows up.

## Todo

Finish lists:
- Gen 3 (RS)
- Gen 4 (BDSP)
- Gen 7 (SM, USUM)
- Gen 8 (SwSh)
