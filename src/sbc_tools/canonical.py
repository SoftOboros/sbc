"""SBCT wrapper canonicalization; distinct from inherited C6 algorithms."""
import json


def canonical_json(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       allow_nan=False, separators=(",", ":")) + "\n").encode("utf-8")
