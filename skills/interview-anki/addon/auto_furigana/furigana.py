"""Turn plain Japanese text into Anki furigana syntax (" 漢字[かんじ]").

Readings can be forced three ways: in the text right after the kanji (御社[おんしゃ]),
as {base|reading} in the text, or through the `readings` mapping passed to furigana().
"""
import os, re, sys

K = "㐀-鿿々〆"
HAS_KANJI = re.compile(f"[{K}]")
RUNS = re.compile(f"[{K}]+|[^{K}]+")
OVERRIDE = re.compile(f"\\{{([^|}}]+)\\|([^}}]+)\\}}|([{K}]+)\\[([^\\]]+)\\]")
MARKUP = re.compile(r"(<[^>]+>|&[#\w]+;)")
# Readings the analyzer gets wrong in interview language.
FIXES = [
    (r"御社(?!\[)", "{御社|おんしゃ}"), (r"日本(?!\[)", "{日本|にほん}"), (r"私(?![\[達])", "{私|わたし}"),
    (r"一人(?!\[)", "{一人|ひとり}"), (r"一回(?!\[)", "{一回|いっかい}"), (r"何(?=[をがか])", "{何|なに}"),
    (r"(?<=\d)日(?![\[|])", "{日|にち}"), (r"(?<=\d)月(?![\[|])", "{月|がつ}"), (r"活(?=か)", "{活|い}"),
    (r"他(?=の)", "{他|ほか}"), (r"か国語", "か{国語|こくご}"), (r"(?<=の)間(?=[、に])", "{間|あいだ}"),
]

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
_tokenizer = None


def hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def ruby(base, reading):
    return f" {base}[{reading}]"


def word(surface, kana):
    """Ruby for one token, with okurigana left outside the brackets."""
    if not HAS_KANJI.search(surface) or not kana:
        return surface
    runs = RUNS.findall(surface)
    pattern = "".join("(.+?)" if HAS_KANJI.match(r) else re.escape(hira(r)) for r in runs)
    m = re.fullmatch(pattern, hira(kana))
    if not m:
        return ruby(surface, hira(kana))
    groups = iter(m.groups())
    return "".join(ruby(r, next(groups)) if HAS_KANJI.match(r) else r for r in runs)


def parse(lines):
    """Return [(surface, kana), ...] for each line, using Janome."""
    global _tokenizer
    if _tokenizer is None:
        from janome.tokenizer import Tokenizer
        _tokenizer = Tokenizer()
    return [[(t.surface, "" if t.reading == "*" else t.reading) for t in _tokenizer.tokenize(line)]
            for line in lines]


def annotate(segment, tokens):
    out, pos = [], 0
    for surface, kana in tokens:
        i = segment.find(surface, pos)
        if i < 0:
            continue
        out.append(segment[pos:i])
        out.append(word(surface, kana))
        pos = i + len(surface)
    out.append(segment[pos:])
    return "".join(out)


def furigana(text, readings=None):
    # Longest bases first, so a reading for 心悦 is not split by one for 心.
    for base, reading in sorted((readings or {}).items(), key=lambda kv: -len(kv[0])):
        text = re.sub(f"(?<![{{|]){re.escape(base)}(?![\\[|])", f"{{{base}|{reading}}}", text)
    for pat, rep in FIXES:
        text = re.sub(pat, rep, text)
    # Markup and forced readings pass through; everything else is analyzed.
    pieces = []
    for part in MARKUP.split(text):
        if MARKUP.fullmatch(part):
            pieces.append(("keep", part))
            continue
        last = 0
        for m in OVERRIDE.finditer(part):
            pieces.append(("text", part[last:m.start()]))
            base, reading = (m[1], m[2]) if m[1] else (m[3], m[4])
            pieces.append(("keep", ruby(base, reading)))
            last = m.end()
        pieces.append(("text", part[last:]))
    texts = [p for kind, p in pieces if kind == "text" and HAS_KANJI.search(p)]
    parsed = iter(parse(texts)) if texts else iter(())
    return "".join(annotate(p, next(parsed)) if kind == "text" and HAS_KANJI.search(p) else p
                   for kind, p in pieces)
