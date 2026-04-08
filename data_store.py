import json
from pathlib import Path
from typing import Any

# =========================
# JSON HELPERS 
# =========================
# Purpose: Open a JSON file and convert its contents into Python data
def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:  # Open the file in read mode (auto-closes after block)
        return json.load(f)                      # Read JSON text and convert it into Python (dict/list/etc.)

# Purpose: Safely convert a value to an integer, If conversion fails (bad type or invalid value), return a default 0 instead
def _as_int(value, default=0) -> int:
    try:
        return int(value)              # Attempt to convert to integer
    except Exception:                  # If conversion fails
        return default                 # Return safe fallback value


def _as_str(value, default="") -> str:
    # Purpose: Safely convert a value to a string, If the value is None, return an empty string, If conversion fails (ALMOST NEVER DOES), return the default.
    try:
        if value is None:
            return ""         # Avoid displaying "None" in the UI
        return str(value)     # Convert any valid value to string
    except Exception:
        return default        # Fallback safety (unlikely to trigger)

def _as_list(value) -> list:
# Ensure the value is a list, If it's not a list (None, dict, string, etc.), return an empty list instead.
    return value if isinstance(value, list) else []

def _as_dict(value) -> dict:
    # Ensure the value is a dict. If it's not a dict (None, list, string, etc.), return an empty dict instead.
    return value if isinstance(value, dict) else {}

def group_by(items, key_name):
    grouped = {}
    for item in items:
        key = item.get(key_name)
        if key is None:
            continue
        grouped.setdefault(key, []).append(item)
    return grouped


def index_by_id(items):
    indexed = {}
    for item in items:
        item_id = item.get("id")
        if item_id is None:
            continue
        indexed[item_id] = item
    return indexed

# =========================
# WEAPONS (UI-SAFE, DATA-ONLY)
# =========================
def make_weapon_ui_safe(raw_weapon: dict) -> dict:
    # Purpose:
    # Take raw weapon data from JSON and normalize it into a clean, consistent structure so the UI never has to deal with missing fields or incorrect types.
    return {
        # --- Basic Identity --- #
        "id": raw_weapon.get("id"),                                 # Keep raw ID (assumed valid)
        "kind": _as_str(raw_weapon.get("kind", "")),                # Ensure string
        "name": _as_str(raw_weapon.get("name", "")),                # Ensure string
        "description": _as_str(raw_weapon.get("description", "")),  # Safe string for UI display

        # --- Core Stats (force numeric safety) --- #
        "rarity": _as_int(raw_weapon.get("rarity", 0)),
        "raw": _as_int(raw_weapon.get("raw", 0)),
        "affinity": _as_int(raw_weapon.get("affinity", 0)),
        "defense": _as_int(raw_weapon.get("defense", 0)),

        # --- Slots / Skills --- #
        "slots": _as_list(raw_weapon.get("slots", [])),             # Always a list
        "specials": _as_list(raw_weapon.get("specials", [])),       # Always a list
        "skills": _as_dict(raw_weapon.get("skills", {})),           # Always a dict

        # --- Advanced / Nested Data (leave raw for now) --- #
        "sharpness": raw_weapon.get("sharpness"),
        "handicraft": raw_weapon.get("handicraft"),
        "crafting": raw_weapon.get("crafting"),
        "series_id": raw_weapon.get("series_id"),
    }

def load_all_weapons(weapons_dir: str | Path = "WEAPONS") -> list[dict]:
    # Purpose: Load every weapon JSON file in the weapons folder and return a single list of cleaned weapons.

    weapons_path = Path(weapons_dir)  # Convert input ("WEAPONS" or Path) into a Path object
    if not weapons_path.exists():     # Fail fast if the folder is missing
        raise FileNotFoundError(f"Missing weapons folder: {weapons_path.resolve()}")

    all_weapons: list[dict] = []      # This will hold every weapon from every file

    for file_path in sorted(weapons_path.glob("*.json")):   # Loop through all weapon JSON files (stable order)
        data = _load_json(file_path)                        # Read/parse JSON file into Python data

        if not isinstance(data, list):                      # Each weapon file must contain a list of weapons
            raise ValueError(f"{file_path.name} should be a LIST, got {type(data)}")

        for w in data:                                      # Each item in the list should be one weapon dict
            if isinstance(w, dict):                         # Ignore bad entries that aren't dictionaries
                all_weapons.append(make_weapon_ui_safe(w))  # Normalize weapon into UI-safe format

    return all_weapons                                      # Combined list of all weapons

# =========================
# ARMOR (UI-SAFE, DATA-ONLY)
# =========================
def make_armor_ui_safe(raw_armor: dict) -> dict:
    # Purpose:
    # Take raw armor data from JSON and normalize it into a clean, consistent structure
    # so the UI never has to deal with missing fields, nested objects, or incorrect types.

    # --- Extract & Normalize Nested Defense --- #
    defense_obj = _as_dict(raw_armor.get("defense", {}))   # Ensure defense is always a dict
    defense_max = _as_int(defense_obj.get("max", 0))       # Extract max defense safely

    return {
        # --- Basic Identity --- #
        "id": raw_armor.get("id"),                                 # Keep raw ID (assumed valid)
        "kind": _as_str(raw_armor.get("kind", "")),                # head / chest / arms / waist / legs
        "name": _as_str(raw_armor.get("name", "")),                # Ensure string
        "description": _as_str(raw_armor.get("description", "")),  # Safe string for UI display

        # --- Core Stats --- #
        "rarity": _as_int(raw_armor.get("rarity", 0)),             # Ensure integer
        "defense": defense_max,                                    # Use normalized max defense value

        # --- Slots / Skills --- #
        "slots": _as_list(raw_armor.get("slots", [])),             # Always a list
        "skills": _as_dict(raw_armor.get("skills", {})),           # Always a dict

        # --- Additional Metadata (leave raw for now) --- #
        "resistances": raw_armor.get("resistances"),
        "set_id": raw_armor.get("set_id"),
        "set_name": raw_armor.get("set_name"),
    }

def load_all_armor(armor_dir: str | Path = "ARMOR") -> list[dict]:
    # Purpose: Load armor data from armor_pieces.json, validate its structure, normalize each armor entry, and return a list of cleaned armor dictionaries.

    armor_path = Path(armor_dir) / "armor_pieces.json"  # Construct full path to armor JSON file

    if not armor_path.exists():                         # Fail fast if file is missing
        raise FileNotFoundError(
            f"Missing armor_pieces.json: {armor_path.resolve()}"
        )

    data = _load_json(armor_path)                       # Read/parse JSON file into Python data

    if not isinstance(data, list):                      # Ensure the file contains a list of armor entries
        raise ValueError(
            f"armor_pieces.json should be a LIST, got {type(data)}"
        )

    # Normalize each valid armor dictionary into UI-safe format
    return [
        make_armor_ui_safe(a)
        for a in data
        if isinstance(a, dict)                          # Ignore invalid entries
    ]

# =========================
# ACCESSORIES / DECORATIONS (DATA-ONLY)
# =========================
def load_all_accessories(accessories_dir: str | Path = "ACCESSORIES") -> list[dict]:
    # Purpose:
    # Load accessories / decorations from ACCESSORIES/accessories.json,
    # validate the file structure, normalize each entry into UI-safe format,
    # and return a list of cleaned accessory dictionaries.

    path = Path(accessories_dir) / "accessories.json"   # Build full path to accessories.json
    if not path.exists():                               # Fail fast if the file is missing
        raise FileNotFoundError(f"Missing accessories.json: {path.resolve()}")

    data = _load_json(path)                             # Read/parse JSON file into Python data
    if not isinstance(data, list):                      # Ensure the file contains a LIST of accessories
        raise ValueError(f"accessories.json should be a LIST, got {type(data)}")

    cleaned: list[dict] = []                            # Holds all normalized accessory entries

    for a in data:                                      # Each item should be one accessory dict
        if not isinstance(a, dict):                     # Skip invalid entries safely
            continue

        cleaned.append({
            # --- Basic Identity --- #
            "id": a.get("id"),                          # Keep raw ID (assumed valid)
            "name": _as_str(a.get("name", "")),         # Ensure string
            "level": _as_int(a.get("level", 0)),        # Ensure integer (deco slot level)

            # --- Rules / Restrictions --- #
            "allowed_on": _as_str(a.get("allowed_on", "")),  # "armor" or "weapon"

            # --- Skills Provided --- #
            "skills": _as_dict(a.get("skills", {})),    # skill_id -> level (always a dict)
        })

    return cleaned                                      # List of cleaned accessories


# =========================
# ONE-CALL LOADER (DATA-ONLY)
# =========================
def load_data(
    weapons_dir: str | Path = "WEAPONS",
    armor_dir: str | Path = "ARMOR",
    accessories_dir: str | Path = "ACCESSORIES",
) -> tuple[list[dict], list[dict], list[dict]]:
    # Purpose:
    # Convenience function to load ALL game data in one call.
    # Returns: (weapons_list, armor_list, accessories_list)

    return (
        load_all_weapons(weapons_dir),                  # Load + normalize all weapons
        load_all_armor(armor_dir),                      # Load + normalize all armor
        load_all_accessories(accessories_dir),          # Load + normalize all accessories/decos
    )

# =========================
# CLASS
# =========================
class DataStore:
    # Purpose: Load all game data once and store it in one place (one object)

    def __init__(self, weapons_dir = "WEAPONS", armor_dir = "ARMOR", accessories_dir = "ACCESSORIES"):
        # 1) Load all cleaned base data
        self.weapons, self.armor, self.accessories = load_data(
            weapons_dir = weapons_dir,
            armor_dir = armor_dir,
            accessories_dir = accessories_dir,
        )

        # 2) Build derived indexes (groupings/lookups)
        self.weapons_by_kind = group_by(self.weapons, "kind")
        self.armor_by_kind = group_by(self.armor, "kind")
        self.accessories_by_allowed_on = group_by(self.accessories, "allowed_on")

        self.weapon_by_id = index_by_id(self.weapons)
        self.armor_by_id = index_by_id(self.armor)
        self.accessory_by_id = index_by_id(self.accessories)