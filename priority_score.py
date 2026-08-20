from dataclasses import dataclass
from time import time

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
    return (
        again_rate * 60
        + again_count * 3
        + recent_again * 5
    )


def get_priority_level(score):
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"


def get_ankiphil_deck_ids():
    deck_ids = []

    for deck in mw.col.decks.all():
        deck_name = deck["name"]

        if deck_name.startswith("Ankiphil"):
            deck_ids.append(deck["id"])

    return deck_ids


def calculate_priority_cards(limit=20):
    thirty_days_ago = int(
        (time() - 30 * 24 * 60 * 60) * 1000
    )

    ankiphil_deck_ids = get_ankiphil_deck_ids()

    if not ankiphil_deck_ids:
        return []

    placeholders = ",".join(
        ["?"] * len(ankiphil_deck_ids)
    )

    query = f"""
        SELECT
            revlog.cid,
            COUNT(*) AS reviews,
            SUM(
                CASE
                    WHEN revlog.ease = 1 THEN 1
                    ELSE 0
                END
            ) AS again_count,
            SUM(
                CASE
                    WHEN revlog.ease = 1
                    AND revlog.id >= ?
                    THEN 1
                    ELSE 0
                END
            ) AS recent_again
        FROM revlog

        INNER JOIN cards
            ON cards.id = revlog.cid

        WHERE
            revlog.ease > 0
            AND cards.did IN ({placeholders})

        GROUP BY revlog.cid

        HAVING COUNT(*) >= 3
    """

    parameters = [
        thirty_days_ago,
        *ankiphil_deck_ids,
    ]

    rows = mw.col.db.all(
        query,
        *parameters,
    )

    results = []

    for card_id, reviews, again_count, recent_again in rows:
        again_count = again_count or 0
        recent_again = recent_again or 0

        again_rate = again_count / reviews

        score = calculate_score(
            again_rate,
            again_count,
            recent_again,
        )

        results.append(
            CardPriority(
                card_id=card_id,
                reviews=reviews,
                again_count=again_count,
                again_rate=again_rate,
                recent_again=recent_again,
                score=score,
            )
        )

    results.sort(
        key=lambda card: card.score,
        reverse=True,
    )

    return results[:limit]


def get_card_text(card_id):
    try:
        card = mw.col.get_card(card_id)
        note = card.note()

        preferred_fields = [
            "Frage",
            "Question",
            "Text",
            "Vorderseite",
            "Front",
        ]

        for field_name in preferred_fields:
            if field_name in note:
                value = note[field_name].strip()

                if value:
                    return value[:160]

        for value in note.values():
            value = value.strip()

            if value:
                return value[:160]

        return "[Kein sinnvoller Kartentext gefunden]"

    except Exception:
        return "[Karte konnte nicht geladen werden]"


def show_priority_cards():
    cards = calculate_priority_cards()

    if not cards:
        showText(
            "AnkiMed konnte keine Ankiphil-Karten mit geeigneten Review-Daten finden."
        )
        return

    text = "ANKIMED – ANKIPHIL PRIORITY CARDS\n\n"

    for position, card in enumerate(cards, start=1):
        card_text = get_card_text(card.card_id)
        level = get_priority_level(card.score)

        text += (
            f"{position}. {level} – Score {card.score:.1f}\n"
            f"{card_text}\n"
            f"Reviews: {card.reviews} | "
            f"Again: {card.again_count} | "
            f"Again-Rate: {card.again_rate:.0%} | "
            f"Again 30d: {card.recent_again}\n\n"
        )

    showText(text)

def open_priority_cards_in_browser():
    cards = calculate_priority_cards(limit=20)

    if not cards:
        showText(
            "AnkiMed konnte keine Priority Cards finden."
        )
        return

    card_ids = [
        str(card.card_id)
        for card in cards
    ]

    search = "cid:" + ",".join(card_ids)

    browser = mw.onBrowse()
    browser.form.searchEdit.lineEdit().setText(search)
    browser.onSearchActivated()
