"""ボードデータの永続化."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from petatto_kanban.models import Board, Card

DATA_FILE_NAME = "board.json"
SCHEMA_VERSION = 4


def get_data_path() -> Path:
    """ユーザーデータディレクトリ内の保存先パスを返す."""
    base = Path.home() / ".petatto-kanban"
    base.mkdir(parents=True, exist_ok=True)
    return base / DATA_FILE_NAME


def _serialize_datetime(value: datetime) -> str:
    return value.isoformat()


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _card_to_dict(card: Card) -> dict[str, Any]:
    return {
        "id": card.id,
        "title": card.title,
        "x": card.x,
        "y": card.y,
        "progress": card.progress,
        "created_at": _serialize_datetime(card.created_at),
        "updated_at": _serialize_datetime(card.updated_at),
    }


def _card_from_dict(data: dict[str, Any]) -> Card:
    return Card(
        id=data["id"],
        title=data["title"],
        x=int(data.get("x", 120)),
        y=int(data.get("y", 120)),
        progress=int(data.get("progress", 0)),
        created_at=_parse_datetime(data["created_at"]),
        updated_at=_parse_datetime(data["updated_at"]),
    )


def _migrate_columns_to_cards(data: dict[str, Any]) -> list[Card]:
    """旧スキーマ（columns）を自由配置 cards に変換する."""
    cards: list[Card] = []
    x_offset = 80
    for column_index, column_data in enumerate(data.get("columns", [])):
        y_offset = 80
        for card_index, card_data in enumerate(column_data.get("cards", [])):
            card = _card_from_dict(
                {
                    **card_data,
                    "x": x_offset + column_index * 260,
                    "y": y_offset + card_index * 130,
                }
            )
            cards.append(card)
    return cards


def board_to_dict(board: Board) -> dict[str, Any]:
    """Board を JSON シリアライズ可能な dict に変換する."""
    return {
        "schema_version": SCHEMA_VERSION,
        "id": board.id,
        "name": board.name,
        "cards": [_card_to_dict(card) for card in board.cards],
        "created_at": _serialize_datetime(board.created_at),
        "updated_at": _serialize_datetime(board.updated_at),
    }


def board_from_dict(data: dict[str, Any]) -> Board:
    """dict から Board を復元する."""
    if "cards" in data:
        cards = [_card_from_dict(card_data) for card_data in data.get("cards", [])]
    else:
        cards = _migrate_columns_to_cards(data)

    return Board(
        id=data["id"],
        name=data["name"],
        cards=cards,
        created_at=_parse_datetime(data["created_at"]),
        updated_at=_parse_datetime(data["updated_at"]),
    )


def load_board(path: Path | None = None) -> Board:
    """保存済みボードを読み込む。存在しない場合はデフォルトボードを返す."""
    target = path or get_data_path()
    if not target.exists():
        return Board.create_default()

    with target.open(encoding="utf-8") as file:
        data = json.load(file)
    return board_from_dict(data)


def save_board(board: Board, path: Path | None = None) -> None:
    """ボードを JSON ファイルに保存する."""
    target = path or get_data_path()
    board.touch()
    payload = board_to_dict(board)
    with target.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
