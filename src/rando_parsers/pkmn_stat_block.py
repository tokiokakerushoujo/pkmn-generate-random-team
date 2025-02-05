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
        "ability1": str,
        "ability2": str,
        "types": list[str],
        "items": list[str],
        "locations": list[str],
    },
)
