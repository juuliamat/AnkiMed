from dataclasses import dataclass
from time import time
import re

from aqt import mw
from aqt.utils import showText
from anki.utils import strip_html


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


def calculate_priority_cards(limit=20):
    thirty_days_ago = int(
        (time() - 30 * 24 * 60 * 60) * 1000
    )

    rows = mw.col.db.all(
        """
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

        WHERE revlog.ease > 0

        GROUP BY revlog.cid

        HAVING COUNT(*) >= 3
        """,
        thirty_days_ago,
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


def get_card_question(card_id):
    card = mw.col.get_card(card_id)

    question = card.question()

    # CSS entfernen
    question = re.sub(
        r"<style.*?>.*?</style>",
        "",
        question,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # HTML-Tags entfernen
    question = strip_html(question)

    # überflüssige Leerzeichen entfernen
    question = re.sub(
        r"\s+",
        " ",
        question,
    ).strip()

    if len(question) > 120:
        question = question[:120] + "..."

    return question


def show_priority_cards():
    cards = calculate_priority_cards()

    if not cards:
        showText(
            "AnkiMed konnte noch keine geeigneten Review-Daten finden."
        )
        return

    text = "ANKIMED – PRIORITY CARDS\n\n"

    for position, card in enumerate(cards, start=1):
        question = get_card_question(card.card_id)
        level = get_priority_level(card.score)

        text += (
            f"{position}. {level} – Score {card.score:.1f}\n"
            f"{question}\n"
            f"Reviews: {card.reviews} | "
            f"Again: {card.again_count} | "
            f"Again-Rate: {card.again_rate:.0%} | "
            f"Again 30d: {card.recent_again}\n\n"
        )

    showText(text)
