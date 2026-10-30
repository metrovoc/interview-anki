# interview-anki

An agent skill that prepares you for a job interview. It predicts the questions from your resume, the job posting and the interview invitation, writes short model answers, and builds an Anki deck that speaks each question aloud and shows its text only with the answer.

For Japanese interviews the deck carries furigana, and a bundled Anki add-on regenerates it whenever you edit the plain-text fields.

## Install

The skill lives in `skills/interview-anki`. Copy that directory into your agent's skills directory:

```sh
git clone https://github.com/metrovoc/interview-anki
cp -r interview-anki/skills/interview-anki ~/.claude/skills/   # Claude Code
cp -r interview-anki/skills/interview-anki ~/.codex/skills/    # Codex
```

The scripts need [uv](https://docs.astral.sh/uv/). Spoken questions need an [ElevenLabs](https://elevenlabs.io) API key in `ELEVENLABS_API_KEY`.

## Use

```
/interview-anki [company] [role or interview]
```

In Codex, write `$interview-anki` instead. Give the agent your resume and the interview invitation, or point it to them.
