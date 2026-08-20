from aqt import mw
from aqt.qt import QAction

from .priority_score import (
    show_priority_cards,
    open_priority_cards_in_browser,
)


def setup_menu():
    menu = mw.form.menuTools.addMenu("AnkiMed")

    priority_action = QAction("Priority Score", mw)
    priority_action.triggered.connect(show_priority_cards)
    menu.addAction(priority_action)

    browser_action = QAction("Priority Cards im Browser öffnen", mw)
    browser_action.triggered.connect(open_priority_cards_in_browser)
    menu.addAction(browser_action)


setup_menu()
