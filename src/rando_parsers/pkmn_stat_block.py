from typing import TypedDict

PkmnStatBlock = TypedDict(
    "PkmnStatBlock",
    {
        "def": int,
        "hp": int,
        "atk": int,
        "spdef": int,
        "spatk": int,
        "spe": int,
        "total": int,
        "species": str,
        "ability1": str | None,  # gen3+ only
        "ability2": str | None,  # gen3+ only
        "ability3": str | None,  # gen5+ only
        "types": list[str],
        "items": list[str] | None,  # doesnt exist in gen1 - items cannot be held
        "locations": list[str],
    },
)
