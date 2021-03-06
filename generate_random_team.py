import argparse
import re


def shuffle_list_x_times(list, count=1167):
    import random
    for _ in range(0, count):
        random.shuffle(list)


def pkmn_has_version_tag(pkmn):
    has_tag_regex = r"\w* \[(\w*\|?)*\]"
    return (re.match(has_tag_regex, pkmn)) is not None


def get_version_tags(pkmn):
    v = re.search(r"\[(\w*\|?)*\]", pkmn)
    return v[0][1:-1].split('|')


def pkmn_matches_version(versions, pkmn):
    return any([ver in versions for ver in get_version_tags(pkmn)]
               ) if versions is not None else True


def generate_list(filename, count):
    team = []
    versions = None
    with open(filename, "r", encoding="utf-8") as pklist:
        pkmn = pklist.readlines()
        shuffle_list_x_times(pkmn, count)
        i = 0
        curr = pkmn[i]
        while len(team) < 6:
            # add pokemon to the final list
            # if it encounters a pkmn with a version exclusive,
            # add it to the list iff it matches the current allowed versions
            if not pkmn_has_version_tag(curr):
                team.append(curr.strip())
            else:
                if versions is None:
                    # set version to the allowed versions
                    versions = get_version_tags(curr)

                if pkmn_matches_version(versions, curr):
                    team.append(curr.strip())

            i = i + 1
            curr = pkmn[i]
    return team


files = [
    "gen1.txt",
    "gen2.txt", "gen2_crystal.txt", "gen2_hgss.txt",
    "gen3.txt", "gen3_emerald.txt", "gen3_oras.txt",
    "gen4.txt", "gen4_pt.txt",
    "gen5.txt", "gen5_b2w2.txt",
    "gen6.txt",
    "gen7.txt", "gen7_u.txt",
    "gen8.txt"
]


def prompt():
    try:
        choice = int(input("""        [ 0]: gen 1 (rby/frlg)
        [ 1]: gen 2 (gs)
        [ 2]: gen 2 (c)
        [ 3]: gen 2 (hgss)
        [ 4]: gen 3 (rs)
        [ 5]: gen 3 (em)
        [ 6]: gen 3 (oras)
        [ 7]: gen 4 (dp)
        [ 8]: gen 4 (pt)
        [ 9]: gen 5 (bw)
        [10]: gen 5 (b2w2)
        [11]: gen 6 (xy)
        [12]: gen 7 (sm)
        [13]: gen 7 (usum)
        [14]: gen 8 (swsh)
        > """))
        if (choice not in range(0, len(files))):
            print("Invalid input.")
            return None
        return f"lists/{files[choice]}"
    except BaseException:
        print("Invalid input.")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser("generate_random_team")
    parser.add_argument(
        "-i",
        "--infile",
        help="List of pokemon to generate a team from",
        type=str)
    parser.add_argument(
        "-c",
        "--count",
        help="Number of times to shuffle the list (default 1167)",
        type=int,
        default=1167)
    parser.add_argument(
        "-o",
        "--outfile",
        help="Destination file to write generated team",
        type=argparse.FileType(
            "w",
            encoding="utf-8"))

    args = parser.parse_args()

    infile = prompt() if args.infile is None else args.infile

    if infile is None:
        exit()

    team = generate_list(infile, args.count)

    if args.outfile:
        args.outfile.write("\n".join(team))
    else:
        print(team)
