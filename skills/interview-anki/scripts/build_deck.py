# /// script
# requires-python = ">=3.10"
# dependencies = ["genanki==0.13.1", "janome==0.5.0"]
# ///
"""Build an Anki package from a deck spec and its audio clips.

  build_deck.py DECK.json --audio DIR --out DECK.apkg

The front of each card plays the question and shows nothing else; the back shows the
question and the answer. A card without a clip shows its question on the front instead.
For "language": "ja" the deck also carries generated furigana fields, which the
auto_furigana add-on keeps in sync after the user edits the plain-text fields.
"""
import argparse, hashlib, os, sys

import genanki

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "addon", "auto_furigana"))
import deckspec

CSS = """
.card { font-family: "Hiragino Sans", "Yu Gothic", "Meiryo", "Noto Sans CJK JP", system-ui, sans-serif;
  font-size: 22px; line-height: 2.1; color: #1d2330; background: #f6f6f2; text-align: left;
  max-width: 40em; margin: 0 auto; padding: 0 0.5em; }
.card.nightMode { color: #e5e7ec; background: #14171d; }
.listen { text-align: center; padding-top: 2em; }
.q { font-weight: 600; color: #6b7182; font-size: 0.85em; }
.nightMode .q { color: #9096a4; }
hr#answer { border: 0; border-top: 1px solid #dfe0dc; margin: 1em 0; }
.nightMode hr#answer { border-top-color: #2b303a; }
rt { font-size: 0.5em; color: #6b7182; font-weight: 400; }
.nightMode rt { color: #9096a4; }
"""


def note_type(furigana):
    q, a = ("furigana:Question Furigana", "furigana:Answer Furigana") if furigana else ("Question", "Answer")
    fields = [{"name": "Question"}, {"name": "Answer"}, {"name": "Audio"}]
    if furigana:
        fields += [{"name": "Question Furigana", "collapsed": True}, {"name": "Answer Furigana", "collapsed": True}]
    # The name and id of the furigana type must match the add-on's config.json.
    return genanki.Model(
        1793131901 if furigana else 1793131903,
        "Interview Q&A (audio)" if furigana else "Interview Q&A (audio, plain)",
        fields=fields,
        templates=[{
            "name": "Listen → Answer",
            "qfmt": f'<div class="listen">{{{{Audio}}}}{{{{^Audio}}}}{{{{{q}}}}}{{{{/Audio}}}}</div>',
            "afmt": f'<div class="q">{{{{{q}}}}}</div><hr id="answer"><div class="a">{{{{{a}}}}}</div>',
        }],
        css=CSS, sort_field_index=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    spec = deckspec.load(a.deck)
    is_ja = spec.get("language") == "ja"
    if is_ja:
        from furigana import furigana
    model = note_type(is_ja)
    deck = genanki.Deck(int(hashlib.sha1(spec["deck"].encode()).hexdigest()[:8], 16), spec["deck"])
    media, missing = [], []
    for section, card in deckspec.cards(spec):
        q, ans = card["q"].replace("\n", "<br>"), card["a"].replace("\n", "<br>")
        clip = os.path.join(a.audio, deckspec.audio_name(spec, card))
        audio = ""
        if os.path.exists(clip):
            media.append(clip)
            audio = f"[sound:{os.path.basename(clip)}]"
        else:
            missing.append(card["id"])
        fields = [q, ans, audio]
        if is_ja:
            fields += [furigana(q, spec.get("readings")), furigana(ans, spec.get("readings"))]
        deck.add_note(genanki.Note(
            model=model, fields=fields, due=len(deck.notes),
            guid=genanki.guid_for(spec["deck"], card["id"]),
            tags=["interview::" + section.replace(" ", "_")]))
    pkg = genanki.Package(deck)
    pkg.media_files = media
    pkg.write_to_file(a.out)
    print(f"{len(deck.notes)} cards, {len(media)} clips -> {a.out}")
    if missing:
        print("no clip for:", ", ".join(missing))


if __name__ == "__main__":
    main()
