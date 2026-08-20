from aqt import mw

from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from .priority_score import (
    calculate_priority_cards,
    get_priority_level,
    show_priority_cards,
    open_priority_cards_in_browser,
    start_priority_session,
)


# =========================================================
# AnkiMed Home
# =========================================================

class AnkiMedHomeDialog(QDialog):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent or mw
        )

        self.setWindowTitle(
            "AnkiMed Home"
        )

        self.resize(
            620,
            520,
        )

        # -------------------------------------------------
        # Hauptlayout
        # -------------------------------------------------

        self.main_layout = (
            QVBoxLayout()
        )

        self.setLayout(
            self.main_layout
        )

        # -------------------------------------------------
        # Titel
        # -------------------------------------------------

        title = QLabel(
            "🩺 AnkiMed"
        )

        title.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 2px;
            """
        )

        self.main_layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Adaptive learning toolkit "
            "for medical students"
        )

        subtitle.setStyleSheet(
            """
            font-size: 13px;
            color: gray;
            margin-bottom: 16px;
            """
        )

        self.main_layout.addWidget(
            subtitle
        )

        # -------------------------------------------------
        # TODAY
        # -------------------------------------------------

        today_title = QLabel(
            "TODAY"
        )

        today_title.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            margin-top: 5px;
            """
        )

        self.main_layout.addWidget(
            today_title
        )

        # -------------------------------------------------
        # Statistik-Box
        # -------------------------------------------------

        stats_frame = QFrame()

        stats_frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        stats_layout = (
            QVBoxLayout(
                stats_frame
            )
        )

        self.priority_label = QLabel()
        self.highest_label = QLabel()
        self.levels_label = QLabel()

        stats_layout.addWidget(
            self.priority_label
        )

        stats_layout.addWidget(
            self.highest_label
        )

        stats_layout.addWidget(
            self.levels_label
        )

        self.main_layout.addWidget(
            stats_frame
        )

        # -------------------------------------------------
        # Priority Session Button
        # -------------------------------------------------

        self.session_button = (
            QPushButton(
                "🔥 Priority Session starten"
            )
        )

        self.session_button.setMinimumHeight(
            45
        )

        self.session_button.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            """
        )

        self.session_button.clicked.connect(
            start_priority_session
        )

        self.main_layout.addWidget(
            self.session_button
        )

        # -------------------------------------------------
        # kleinere Buttons
        # -------------------------------------------------

        button_row = QHBoxLayout()

        score_button = QPushButton(
            "📊 Priority Score"
        )

        score_button.clicked.connect(
            show_priority_cards
        )

        browser_button = QPushButton(
            "🗂 Browser"
        )

        browser_button.clicked.connect(
            open_priority_cards_in_browser
        )

        button_row.addWidget(
            score_button
        )

        button_row.addWidget(
            browser_button
        )

        self.main_layout.addLayout(
            button_row
        )

        # -------------------------------------------------
        # Refresh
        # -------------------------------------------------

        refresh_button = QPushButton(
            "🔄 Dashboard aktualisieren"
        )

        refresh_button.clicked.connect(
            self.refresh_stats
        )

        self.main_layout.addWidget(
            refresh_button
        )

        # -------------------------------------------------
        # TRAIN
        # -------------------------------------------------

        train_title = QLabel(
            "TRAIN"
        )

        train_title.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            margin-top: 18px;
            """
        )

        self.main_layout.addWidget(
            train_title
        )

        coming_soon = QLabel(
            "🧠 DD Trainer\n"
            "💊 Therapy Trainer\n"
            "🧪 Lab Trainer\n"
            "🦠 Antibiotics Matrix"
        )

        coming_soon.setStyleSheet(
            """
            color: gray;
            line-height: 1.4;
            """
        )

        self.main_layout.addWidget(
            coming_soon
        )

        # -------------------------------------------------
        # Progress
        # -------------------------------------------------

        progress_title = QLabel(
            "PROGRESS"
        )

        progress_title.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            margin-top: 18px;
            """
        )

        self.main_layout.addWidget(
            progress_title
        )

        progress_placeholder = QLabel(
            "📉 Weakness Radar     Coming soon\n"
            "🎯 M2 Countdown       Coming soon\n"
            "🗺 Progress Map       Coming soon"
        )

        progress_placeholder.setStyleSheet(
            "color: gray;"
        )

        self.main_layout.addWidget(
            progress_placeholder
        )

        # -------------------------------------------------
        # initial Daten laden
        # -------------------------------------------------

        self.refresh_stats()


    # =====================================================
    # Dashboard aktualisieren
    # =====================================================

    def refresh_stats(self):

        cards = (
            calculate_priority_cards(
                limit=20
            )
        )

        if not cards:

            self.priority_label.setText(
                "🔥 Priority Cards: 0"
            )

            self.highest_label.setText(
                "Highest Score: –"
            )

            self.levels_label.setText(
                "Keine geeigneten "
                "Karten gefunden."
            )

            return

        # -------------------------------------------------
        # Highest Score
        # -------------------------------------------------

        highest_score = max(
            card.score
            for card in cards
        )

        # -------------------------------------------------
        # Level zählen
        # -------------------------------------------------

        level_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }

        for card in cards:

            level = (
                get_priority_level(
                    card.score
                )
            )

            level_counts[level] += 1

        # -------------------------------------------------
        # Anzeigen
        # -------------------------------------------------

        self.priority_label.setText(
            f"🔥 Priority Cards: "
            f"{len(cards)}"
        )

        self.highest_label.setText(
            f"Highest Score: "
            f"{highest_score:.1f}"
        )

        self.levels_label.setText(
            f"🔴 CRITICAL: "
            f"{level_counts['CRITICAL']}     "
            f"🟠 HIGH: "
            f"{level_counts['HIGH']}     "
            f"🟡 MEDIUM: "
            f"{level_counts['MEDIUM']}     "
            f"🟢 LOW: "
            f"{level_counts['LOW']}"
        )


# =========================================================
# Dashboard öffnen
# =========================================================

def show_ankimed_home():

    dialog = AnkiMedHomeDialog(
        mw
    )

    dialog.exec()
