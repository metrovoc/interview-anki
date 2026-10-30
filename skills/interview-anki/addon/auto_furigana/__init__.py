"""Keep furigana fields in sync with plain-text source fields.

config.json maps a note type to {source field: furigana field} and lists forced readings.
A furigana field is rewritten when its source field loses focus in the editor, when a note
is added, after each sync, and from Tools > Regenerate Furigana.
"""
from anki.hooks import note_will_be_added
from aqt import gui_hooks, mw
from aqt.qt import QAction
from aqt.utils import tooltip

from .furigana import furigana


def config():
    return mw.addonManager.getConfig(__name__) or {}


def fill(note):
    cfg = config()
    changed = False
    for src, dst in cfg.get("note_types", {}).get(note.note_type()["name"], {}).items():
        if src in note and dst in note:
            value = furigana(note[src], cfg.get("readings"))
            if note[dst] != value:
                note[dst] = value
                changed = True
    return changed


def on_unfocus(changed, note, idx):
    mapping = config().get("note_types", {}).get(note.note_type()["name"], {})
    if note.note_type()["flds"][idx]["name"] not in mapping:
        return changed
    return fill(note) or changed


def regenerate_all(*_args, quiet=False):
    updated = []
    for type_name in config().get("note_types", {}):
        model = mw.col.models.by_name(type_name)
        if not model:
            continue
        for nid in mw.col.models.nids(model):
            note = mw.col.get_note(nid)
            if fill(note):
                updated.append(note)
    if updated:
        mw.col.update_notes(updated)
    if updated or not quiet:
        tooltip(f"Furigana updated on {len(updated)} notes")


gui_hooks.editor_did_unfocus_field.append(on_unfocus)
note_will_be_added.append(lambda col, note, deck_id: fill(note))
gui_hooks.sync_did_finish.append(lambda: regenerate_all(quiet=True))

action = QAction("Regenerate Furigana", mw)
action.triggered.connect(regenerate_all)
mw.form.menuTools.addAction(action)
