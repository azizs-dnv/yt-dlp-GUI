import json
from typing import Any, Dict

from config import HISTORY_FILE


def load_history(default_stats: Dict[str, int]) -> Dict[str, int]:
    if not HISTORY_FILE.exists():
        return default_stats.copy()

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        stats = data.get("stats", default_stats)
        return {**default_stats, **stats}
    except Exception:
        return default_stats.copy()


def save_history(stats: Dict[str, int], entry: Dict[str, Any]) -> None:
    data = {"stats": stats, "entries": []}
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            data = {"stats": stats, "entries": []}

    data["stats"] = stats
    if "entries" not in data:
        data["entries"] = []
    data["entries"].insert(0, entry)
    data["entries"] = data["entries"][:200]

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
    except Exception:
        pass
