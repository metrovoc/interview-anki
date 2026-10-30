"""Load and check a deck spec, and name its audio clips. Shared by tts.py and build_deck.py."""
import hashlib, json, re


def load(path):
    spec = json.load(open(path, encoding="utf-8"))
    ids = set()
    for section in spec["sections"]:
        for card in section["cards"]:
            if not re.fullmatch(r"[a-z0-9-]+", card["id"]):
                raise SystemExit(f"card id must be lowercase letters, digits and hyphens: {card['id']!r}")
            if card["id"] in ids:
                raise SystemExit(f"duplicate card id: {card['id']}")
            ids.add(card["id"])
    return spec


def cards(spec):
    for section in spec["sections"]:
        for card in section["cards"]:
            yield section["name"], card


def audio_name(spec, card):
    """Changes whenever the question text changes, so Anki never keeps a stale clip."""
    deck = hashlib.sha1(spec["deck"].encode()).hexdigest()[:6]
    text = hashlib.sha1(card["q"].encode()).hexdigest()[:8]
    return f"iv_{deck}_{card['id']}_{text}.mp3"
