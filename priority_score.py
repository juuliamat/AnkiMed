from dataclasses import dataclass
from time import time
import html
import re

import aqt
from aqt import mw
from aqt.utils import showText


@dataclass
class CardPriority:
    card_id: int
    reviews: int
    again_count: int
    again_rate: float
    recent_again: int
    score: float


def calculate_score(again_rate, again_count, recent_again):
    return again_rate * 60 + again_count * 3 + recent_again * 5


def get_priority_level(score):
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def clean_card_text(text):
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\{\{c\d+::(.*?)(?:::[^}]*)?\}\}", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:180] + "..." if len(text) > 180 else text


def get_ankiphil_deck_ids():
    return [
        deck["id"]
        for deck in mw.col.decks.all()
        if deck["name"].casefold().startswith("ankiphil")
    ]


def calculate_priority_cards(limit=20):
    thirty_days_ago = int((time() - 30 * 24 * 60 * 60) * 1000)
    deck_ids = get_ankiphil_deck_ids()
    if not deck_ids:
        return []

    placeholders = ",".join(["?"] * len(deck_ids))
    rows = mw.col.db.all(
        f"""
        SELECT revlog.cid, COUNT(*) AS reviews,
               SUM(CASE WHEN revlog.ease = 1 THEN 1 ELSE 0 END),
               SUM(CASE WHEN revlog.ease = 1 AND revlog.id >= ? THEN 1 ELSE 0 END)
        FROM revlog
        INNER JOIN cards ON cards.id = revlog.cid
        WHERE revlog.ease > 0
          AND (CASE WHEN cards.odid != 0 THEN cards.odid ELSE cards.did END)
              IN ({placeholders})
        GROUP BY revlog.cid
        HAVING COUNT(*) >= 3
        """,
        thirty_days_ago,
        *deck_ids,
    )

    results = []
    for card_id, reviews, again_count, recent_again in rows:
        again_count = again_count or 0
        recent_again = recent_again or 0
        again_rate = again_count / reviews
        results.append(
            CardPriority(
                card_id=card_id,
                reviews=reviews,
                again_count=again_count,
                again_rate=again_rate,
                recent_again=recent_again,
                score=calculate_score(again_rate, again_count, recent_again),
            )
        )
    results.sort(key=lambda card: card.score, reverse=True)
    return results[:limit]


def get_card_text(card_id):
    try:
        note = mw.col.get_card(card_id).note()
        for field_name in ("Frage", "Question", "Text", "Vorderseite", "Front"):
            if field_name in note and note[field_name].strip():
                return clean_card_text(note[field_name])
        for value in note.values():
            if value.strip():
                return clean_card_text(value)
        return "[Kein sinnvoller Kartentext gefunden]"
    except Exception:
        return "[Karte konnte nicht geladen werden]"


def show_priority_cards():
    cards = calculate_priority_cards(limit=20)
    if not cards:
        showText("AnkiMed konnte keine Ankiphil-Karten mit geeigneten Review-Daten finden.")
        return

    lines = ["ANKIMED – ANKIPHIL PRIORITY CARDS", ""]
    for position, card in enumerate(cards, start=1):
        lines.extend(
            [
                f"{position}. {get_priority_level(card.score)} – Score {card.score:.1f}",
                "",
                get_card_text(card.card_id),
                "",
                f"Reviews: {card.reviews} | Again: {card.again_count} | "
                f"Again-Rate: {card.again_rate:.0%} | Again 30d: {card.recent_again}",
                "",
            ]
        )
    showText("\n".join(lines))


def get_priority_search(limit=20):
    cards = calculate_priority_cards(limit=limit)
    return "cid:" + ",".join(str(card.card_id) for card in cards) if cards else None


def open_priority_cards_in_browser():
    search = get_priority_search(limit=20)
    if not search:
        showText("AnkiMed konnte keine Priority Cards finden.")
        return
    aqt.dialogs.open("Browser", mw, search=(search,))


def start_priority_session():
    search = get_priority_search(limit=20)
    if not search:
        showText("AnkiMed konnte keine Priority Cards finden.")
        return
    from aqt.filtered_deck import FilteredDeckConfigDialog

    FilteredDeckConfigDialog(mw, search=search)
