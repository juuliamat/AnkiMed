from dataclasses import dataclass
from time import time
import html
import re
import aqt

from aqt import mw
from aqt.utils import showText


# ---------------------------------------------------------
# Datenstruktur
# ---------------------------------------------------------

@dataclass
class CardPriority:
    card_id: int
    reviews: int
    again_count: int
    again_rate: float
    recent_again: int
    score: float


# ---------------------------------------------------------
# Priority Score
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Kartentext bereinigen
# ---------------------------------------------------------

def clean_card_text(text):

    # <br>, <br/> usw. in Leerzeichen umwandeln
    text = re.sub(
        r"<br\s*/?>",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    # alle übrigen HTML-Tags entfernen
    text = re.sub(
        r"<[^>]+>",
        "",
        text,
    )

    # HTML-Sonderzeichen zurückwandeln
    # Beispiel: &gt; → >
    text = html.unescape(text)

    # Cloze-Syntax lesbar machen
    # Beispiel:
    # {{c1::Praziquantel::Therapie}}
    # → Praziquantel
    text = re.sub(
        r"\{\{c\d+::(.*?)(?:::[^}]*)?\}\}",
        r"\1",
        text,
    )

    # mehrere Leerzeichen zusammenfassen
    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    # Text für Übersicht kürzen
    if len(text) > 180:
        text = text[:180] + "..."

    return text


# ---------------------------------------------------------
# Ankiphil-Decks finden
# ---------------------------------------------------------

def get_ankiphil_deck_ids():

    deck_ids = []

    for deck in mw.col.decks.all():

        deck_name = deck["name"]

        if deck_name.startswith("Ankiphil"):
            deck_ids.append(deck["id"])

    return deck_ids


# ---------------------------------------------------------
# Karten analysieren
# ---------------------------------------------------------

def calculate_priority_cards(limit=20):

    # Zeitpunkt vor 30 Tagen
    # revlog.id arbeitet mit Millisekunden
    thirty_days_ago = int(
        (time() - 30 * 24 * 60 * 60) * 1000
    )

    ankiphil_deck_ids = get_ankiphil_deck_ids()

    if not ankiphil_deck_ids:
        return []

    # Für SQL entsteht z.B.:
    #
    # ?, ?, ?, ?
    #
    # je nachdem, wie viele Ankiphil-Decks gefunden wurden
    placeholders = ",".join(
        ["?"] * len(ankiphil_deck_ids)
    )

    query = f"""
        SELECT
            revlog.cid,

            COUNT(*) AS reviews,

            SUM(
                CASE
                    WHEN revlog.ease = 1
                    THEN 1
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

        GROUP BY
            revlog.cid

        HAVING
            COUNT(*) >= 3
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

    for (
        card_id,
        reviews,
        again_count,
        recent_again,
    ) in rows:

        again_count = again_count or 0
        recent_again = recent_again or 0

        again_rate = (
            again_count / reviews
        )

        score = calculate_score(
            again_rate,
            again_count,
            recent_again,
        )

        card_priority = CardPriority(
            card_id=card_id,
            reviews=reviews,
            again_count=again_count,
            again_rate=again_rate,
            recent_again=recent_again,
            score=score,
        )

        results.append(
            card_priority
        )

    # Höchster Priority Score zuerst
    results.sort(
        key=lambda card: card.score,
        reverse=True,
    )

    return results[:limit]


# ---------------------------------------------------------
# Kartentext holen
# ---------------------------------------------------------

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

        # Erst nach typischen Fragefeldern suchen
        for field_name in preferred_fields:

            if field_name in note:

                value = note[field_name].strip()

                if value:
                    return clean_card_text(value)

        # Falls diese Feldnamen nicht existieren:
        # erstes nicht-leeres Feld verwenden
        for value in note.values():

            value = value.strip()

            if value:
                return clean_card_text(value)

        return "[Kein sinnvoller Kartentext gefunden]"

    except Exception:

        return "[Karte konnte nicht geladen werden]"


# ---------------------------------------------------------
# Priority Cards anzeigen
# ---------------------------------------------------------

def show_priority_cards():

    cards = calculate_priority_cards(
        limit=20
    )

    if not cards:

        showText(
            "AnkiMed konnte keine Ankiphil-Karten "
            "mit geeigneten Review-Daten finden."
        )

        return

    text = (
        "ANKIMED – ANKIPHIL PRIORITY CARDS\n"
        "\n"
    )

    for position, card in enumerate(
        cards,
        start=1,
    ):

        card_text = get_card_text(
            card.card_id
        )

        level = get_priority_level(
            card.score
        )

        text += (
            f"{position}. "
            f"{level} – "
            f"Score {card.score:.1f}\n"
            "\n"
            f"{card_text}\n"
            "\n"
            f"Reviews: {card.reviews} | "
            f"Again: {card.again_count} | "
            f"Again-Rate: "
            f"{card.again_rate:.0%} | "
            f"Again 30d: "
            f"{card.recent_again}"
            "\n\n"
        )

    showText(text)


# ---------------------------------------------------------
# Suchstring für Priority Cards erstellen
# ---------------------------------------------------------

def get_priority_search(limit=20):

    cards = calculate_priority_cards(
        limit=limit
    )

    if not cards:
        return None

    card_ids = [
        str(card.card_id)
        for card in cards
    ]

    search = (
        "cid:"
        + ",".join(card_ids)
    )

    return search


# ---------------------------------------------------------
# Priority Cards im Browser öffnen
# ---------------------------------------------------------

def open_priority_cards_in_browser():

    search = get_priority_search(
        limit=20
    )

    if not search:

        showText(
            "AnkiMed konnte keine Priority Cards finden."
        )

        return

    aqt.dialogs.open(
        "Browser",
        mw,
        search=(search,),
    )
