from aqt import mw
from aqt.qt import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from .priority_score import (
    calculate_priority_cards,
    get_priority_level,
    open_priority_cards_in_browser,
    show_priority_cards,
    start_priority_session,
)
from .weakness_radar import get_weakness_summary, show_weakness_radar


class AnkiMedHomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("AnkiMed Home")
        self.resize(680, 590)
        layout = QVBoxLayout(self)

        title = QLabel("🩺 AnkiMed")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(QLabel("Dein persönliches Ankiphil-Lerndashboard"))

        priority = calculate_priority_cards(limit=20)
        top_score = priority[0].score if priority else 0
        priority_box = self._box(
            "🔥 Priority Cards",
            f"{len(priority)} Karten bereit · höchste Stufe: {get_priority_level(top_score) if priority else '–'}",
        )
        button_row = QHBoxLayout()
        for label, callback in (
            ("Ranking anzeigen", show_priority_cards),
            ("Im Browser öffnen", open_priority_cards_in_browser),
            ("Session starten", start_priority_session),
        ):
            button = QPushButton(label)
            button.clicked.connect(callback)
            button_row.addWidget(button)
        priority_box.layout().addLayout(button_row)
        layout.addWidget(priority_box)

        weakness_box = self._box("🎯 Weakness Radar", get_weakness_summary(limit=3))
        weakness_button = QPushButton("Schwächen-Ranking anzeigen")
        weakness_button.clicked.connect(show_weakness_radar)
        weakness_box.layout().addWidget(weakness_button)
        layout.addWidget(weakness_box)

        info_box = self._box("Demnächst", "M2 Countdown · Progress Map · Trainer")
        layout.addWidget(info_box)
        layout.addStretch()

        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

    @staticmethod
    def _box(heading, summary):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("QFrame { padding: 8px; } QLabel { padding: 0; }")
        box = QVBoxLayout(frame)
        label = QLabel(heading)
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        box.addWidget(label)
        summary_label = QLabel(summary)
        summary_label.setWordWrap(True)
        box.addWidget(summary_label)
        return frame


_home_dialog = None


def show_ankimed_home():
    global _home_dialog
    _home_dialog = AnkiMedHomeDialog(mw)
    _home_dialog.show()
    _home_dialog.raise_()
    _home_dialog.activateWindow()
