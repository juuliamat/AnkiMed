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


def calculate_priority_cards(limit=20):
    thirty_days_ago = int(
        (time() - 30 * 24 * 60 * 60) * 1000
    )

    rows = mw.col.db.all(
        """
        SELECT
            cid,
            COUNT(*) AS reviews,
            SUM(
                CASE
                    WHEN ease = 1 THEN 1
                    ELSE 0
                END
            ) AS again_count,
            SUM(
                CASE
                    WHEN ease = 1 AND id >= ? THEN 1
                    ELSE 0
                END
            ) AS recent_again
        FROM revlog
        WHERE ease > 0
        GROUP BY cid
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
    try:
        card = mw.col.get_card(card_id)
        question = card.question()

        question = (
            question
            .replace("<br>", " ")
            .replace("<br/>", " ")
            .replace("<br />", " ")
        )

        if len(question) > 120:
            question = question[:120] + "..."

        return question

    except Exception:
        return "[Karte konnte nicht geladen werden]"


def show_priority_cards():
    cards = calculate_priority_cards()

    if not cards:
        showText(
            "AnkiMed konnte noch keine geeigneten Review-Daten finden."
        )
        return

    html = """
    <h1>🩺 AnkiMed</h1>
    <h2>🔥 Priority Cards</h2>

    <p>
        Ranking deiner aktuell problematischsten Karten.
    </p>

    <table cellpadding="7" cellspacing="0">
        <tr>
            <th>#</th>
            <th>Score</th>
            <th>Level</th>
            <th>Karte</th>
            <th>Reviews</th>
            <th>Again</th>
            <th>Again-Rate</th>
            <th>Again 30d</th>
        </tr>
    """

    for position, card in enumerate(cards, start=1):
        question = get_card_question(card.card_id)
        level = get_priority_level(card.score)

        html += f"""
        <tr>
            <td>{position}</td>
            <td><b>{card.score:.1f}</b></td>
            <td>{level}</td>
            <td>{question}</td>
            <td>{card.reviews}</td>
            <td>{card.again_count}</td>
            <td>{card.again_rate:.0%}</td>
            <td>{card.recent_again}</td>
        </tr>
        """

    html += "</table>"

    showText(html)
