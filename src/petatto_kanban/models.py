"""ドメインモデル定義."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


@dataclass
class Card:
    """カンバン上の1枚のタスクカード."""

    title: str
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    order: int = 0
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    def touch(self) -> None:
        """更新日時を現在時刻に更新する."""
        self.updated_at = _utc_now()


@dataclass
class Column:
    """カンバン列（レーン）."""

    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    order: int = 0
    cards: list[Card] = field(default_factory=list)


@dataclass
class Board:
    """カンバンボード."""

    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    columns: list[Column] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    def touch(self) -> None:
        """更新日時を現在時刻に更新する."""
        self.updated_at = _utc_now()

    @classmethod
    def create_default(cls, name: str = "My Board") -> Board:
        """デフォルト3列のボードを生成する."""
        return cls(
            name=name,
            columns=[
                Column(name="To Do", order=0),
                Column(name="In Progress", order=1),
                Column(name="Done", order=2),
            ],
        )
