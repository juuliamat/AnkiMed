from aqt import mw
from aqt.utils import showText


def show_priority_cards():
    rows = mw.col.db.all(
        """
        SELECT cid, ease
        FROM revlog
        LIMIT 10
        """
    )

    showText(str(rows))
