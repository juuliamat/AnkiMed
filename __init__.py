from aqt import mw
from aqt.qt import QAction

from .home import show_ankimed_home
from .priority_score import (
    open_priority_cards_in_browser,
    show_priority_cards,
    start_priority_session,
)
from .weakness_radar import show_weakness_radar


def setup_menu():
    menu = mw.form.menuTools.addMenu("AnkiMed")

    home_action = QAction("AnkiMed Home", mw)
    home_action.triggered.connect(show_ankimed_home)
    menu.addAction(home_action)

    menu.addSeparator()

    priority_action = QAction("Priority Score", mw)
    priority_action.triggered.connect(show_priority_cards)
    menu.addAction(priority_action)

    browser_action = QAction("Priority Cards im Browser öffnen", mw)
    browser_action.triggered.connect(open_priority_cards_in_browser)
    menu.addAction(browser_action)

    session_action = QAction("Priority Session starten", mw)
    session_action.triggered.connect(start_priority_session)
    menu.addAction(session_action)

    menu.addSeparator()

    weakness_action = QAction("Weakness Radar", mw)
    weakness_action.triggered.connect(show_weakness_radar)
    menu.addAction(weakness_action)


setup_menu()
