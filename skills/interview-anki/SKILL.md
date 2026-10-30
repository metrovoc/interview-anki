---
name: interview-anki
description: Prepare a candidate for an upcoming job interview. Predict its questions from the resume, the role, the company and the interview invitation, write short model answers, and drill them in an Anki deck that speaks each question aloud and hides its text until the answer is shown. Use for interview prep, predicted interview questions, mock-interview drills, or turning interview Q&A into Anki cards.
argument-hint: "[company] [role or interview]"
---

# Interview prep with Anki

Rehearse the interview as it will happen: the candidate hears a question, never reads it, and answers from memory in their own words.

## Evidence

- Gather everything about this interview: the resume the candidate sent, the job posting, the company's own pages, and the invitation and scheduling messages (date, length, language, format and who interviews).
- Job boards often render their content with JavaScript. When a fetch returns only navigation, read the page in a real browser.
- Who interviews decides the depth. A recruiter or a casual first meeting (such as a Japanese カジュアル面談) asks about motivation, experience and fit; an engineer asks technical follow-ups. If the evidence does not say, ask the user before writing technical questions.

## Questions and answers

- Write 50–100 questions unless the user asks for another number. Group them by theme in the order the interview runs: opening, motivation and company fit, each experience on the resume, skills, personality, logistics, any part in a second language the posting requires, and the questions the candidate asks at the end.
- Predict what this interviewer would plausibly ask, from the posting's stated values, products and requirements and from every line of the resume.
- Keep each model answer short enough to memorize, one to three sentences, in the interview's language and register, grounded in the evidence. Where an answer must assume something the evidence does not show, such as a start date, visa status, a failure story or other applications, write a plausible answer and list every such assumption for the user.
- The candidate will rewrite the answers in their own words, so keep all text plain: no inline readings, markup or formatting.

## Deck spec

Write the deck as JSON; [examples/deck.json](examples/deck.json) is a complete example.

```json
{
  "deck": "Example Corp interview",
  "language": "ja",
  "readings": {"山田花子": "やまだはなこ"},
  "sections": [{"name": "志望動機", "cards": [{"id": "why-us", "q": "…", "a": "…"}]}]
}
```

- `id` is a stable slug of lowercase letters, digits and hyphens. It keeps a card's identity and review history across rebuilds; never renumber or reuse one.
- `language` is the interview's language code. `"ja"` adds furigana to every kanji. `readings` forces readings the analyzer gets wrong, such as personal names.
- A line break in `a` becomes a line break on the card.

## Audio

Run the scripts with `uv run`, which installs their dependencies.

1. Load the user's ElevenLabs API key from their secret store into `ELEVENLABS_API_KEY` for each command only. Never print it.
2. Run `scripts/tts.py models --language <code>` and use the newest model it lists. Model names change often; never pick one from memory.
3. Run `scripts/tts.py voices --language <code>` and pick a voice that sounds like the likely interviewer: conversational and professional, native in the interview's language.
4. Run `scripts/tts.py synth deck.json --voice <id> --model <id> --out audio`. Each clip is named after its question's text, so a changed question gets a new clip, and existing clips are kept. Delete the folder to switch voice or model.
5. Transcribe every clip with speech-to-text and compare it with its question. Accept differences that are only homophones; regenerate any other mismatch.

## Build and deliver

```sh
uv run scripts/build_deck.py deck.json --audio audio --out deck.apkg
uv run scripts/package_addon.py auto-furigana.ankiaddon   # Japanese decks only
```

- The front of each card plays its question and shows nothing else; the back shows the question and the answer. A card without a clip shows its question on the front.
- Before touching any Anki installation, ask the user on which computer they study and edit in Anki. Deliver the files there: they install the add-on with Tools > Add-ons > Install from file, restart Anki, then open the package.
- Never write to a collection while Anki is running. Avoid changing note types inside an existing collection: it forces a one-way full sync.
- Rebuilding and importing again updates the existing cards and keeps their reviews. Anki replaces a note only when the package's copy is newer, so answers the user has edited in Anki since the last import stay as they are.

## Editing

- The user edits the plain-text Question and Answer fields. In Japanese decks the auto_furigana add-on rewrites the collapsed furigana fields when a field loses focus, when a note is added and after each sync; Tools > Regenerate Furigana updates every note at once. Edits made on a phone get their furigana at the next sync on a computer with the add-on.
- A wrong reading is fixed by writing the right one after the kanji in the field, as in `御社[おんしゃ]`, or for every card through `readings` in the add-on's config.
- Change questions in the deck spec, then synthesize and rebuild, so each card's audio matches its text.
