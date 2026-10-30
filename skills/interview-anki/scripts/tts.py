# /// script
# requires-python = ">=3.10"
# ///
"""ElevenLabs text-to-speech for interview questions. Reads the key from ELEVENLABS_API_KEY.

  tts.py models [--language ja]               TTS models, as the API lists them
  tts.py voices --language ja [--limit 30]    shared-library voices for a language, most used first
  tts.py synth DECK.json --voice ID --model ID --out DIR
                                              one clip per question; existing clips are kept
"""
import argparse, json, os, sys, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deckspec

API = "https://api.elevenlabs.io"


def call(path, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("models")
    m.add_argument("--language")
    v = sub.add_parser("voices")
    v.add_argument("--language", required=True)
    v.add_argument("--limit", type=int, default=30)
    s = sub.add_parser("synth")
    s.add_argument("deck")
    s.add_argument("--voice", required=True)
    s.add_argument("--model", required=True)
    s.add_argument("--out", required=True)
    a = ap.parse_args()

    if a.cmd == "models":
        for model in json.loads(call("/v1/models")):
            langs = {l["language_id"] for l in model.get("languages", [])}
            if model.get("can_do_text_to_speech") and (not a.language or a.language in langs):
                print(model["model_id"], "|", model["name"])
    elif a.cmd == "voices":
        query = urllib.parse.urlencode({"language": a.language, "page_size": a.limit,
                                        "sort": "usage_character_count_1y"})
        for voice in json.loads(call("/v1/shared-voices?" + query))["voices"]:
            print(voice["voice_id"], "|", voice["name"], "|", voice.get("gender"), voice.get("age"),
                  voice.get("accent"), voice.get("use_case"), "|",
                  (voice.get("description") or "").replace("\n", " ")[:90])
    else:
        spec = deckspec.load(a.deck)
        os.makedirs(a.out, exist_ok=True)
        for _, card in deckspec.cards(spec):
            path = os.path.join(a.out, deckspec.audio_name(spec, card))
            if os.path.exists(path):
                continue
            audio = call(f"/v1/text-to-speech/{a.voice}?output_format=mp3_44100_128",
                         {"text": card["q"], "model_id": a.model})
            open(path, "wb").write(audio)
            print("wrote", os.path.basename(path))


if __name__ == "__main__":
    main()
