from aqt import mw
from aqt.qt import QAction

from .priority_score import show_priority_cards


def setup_menu():
    menu = mw.form.menuTools.addMenu("AnkiMed")

    priority_action = QAction("Priority Score", mw)
    priority_action.triggered.connect(show_priority_cards)

    menu.addAction(priority_action)


setup_menu()
