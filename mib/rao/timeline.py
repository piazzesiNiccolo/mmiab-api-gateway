from datetime import datetime
from typing import List


class Timeline:
    def __init__(
        self,
        sent: List[int] = [],
        received: List[int] = [],
        year: int = datetime.today().year,
        month: int = datetime.today().month,
        **kwargs
    ):
        self.sent = sent
        self.received = received
        self.year = year
        self.month = month

    @staticmethod
    def build_from_json(**kwargs):
        return Timeline(**kwargs)
