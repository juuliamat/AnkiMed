from aqt import mw
from aqt.qt import QAction

from .priority_score import (
    show_priority_cards,
    open_priority_cards_in_browser,
    start_priority_session,
)

from .home import show_ankimed_home


def setup_menu():
    menu = mw.form.menuTools.addMenu("AnkiMed")

    # -----------------------------------------------------
    # AnkiMed Home
    # -----------------------------------------------------

    home_action = QAction(
        "AnkiMed Home",
        mw,
    )

    home_action.triggered.connect(
        show_ankimed_home
    )

    menu.addAction(
        home_action
    )

    # Trennlinie
    menu.addSeparator()

    # -----------------------------------------------------
    # Priority Score
    # -----------------------------------------------------

    priority_action = QAction(
        "Priority Score",
        mw,
    )

    priority_action.triggered.connect(
        show_priority_cards
    )

    menu.addAction(
        priority_action
    )

    # -----------------------------------------------------
    # Priority Cards im Browser
    # -----------------------------------------------------

    browser_action = QAction(
        "Priority Cards im Browser öffnen",
        mw,
    )

    browser_action.triggered.connect(
        open_priority_cards_in_browser
    )

    menu.addAction(
        browser_action
    )

    # -----------------------------------------------------
    # Priority Session
    # -----------------------------------------------------

    session_action = QAction(
        "Priority Session starten",
        mw,
    )

    session_action.triggered.connect(
        start_priority_session
    )

    menu.addAction(
        session_action
    )


setup_menu()
