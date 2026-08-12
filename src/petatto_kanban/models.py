"""ドメインモデル定義."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from uuid import uuid4

from petatto_kanban.progress import clamp_progress


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


@dataclass
class Card:
    """画面上の1枚のタスクカード（自由配置）."""

    title: str
    id: str = field(default_factory=lambda: str(uuid4()))
    x: int = 120
    y: int = 120
    progress: int = 0
    due_date: date | None = None
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        self.progress = clamp_progress(self.progress)

    def touch(self) -> None:
        """更新日時を現在時刻に更新する."""
        self.updated_at = _utc_now()


@dataclass
class Board:
    """カンバンボード（オーバーレイ上のカード集合）."""

    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    cards: list[Card] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    def touch(self) -> None:
        """更新日時を現在時刻に更新する."""
        self.updated_at = _utc_now()

    @classmethod
    def create_default(cls, name: str = "My Board") -> Board:
        """空のボードを生成する."""
        return cls(name=name, cards=[])

    def remove_card(self, card_id: str) -> None:
        self.cards = [card for card in self.cards if card.id != card_id]

    def find_card(self, card_id: str) -> Card | None:
        return next((card for card in self.cards if card.id == card_id), None)
