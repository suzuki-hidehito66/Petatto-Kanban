"""ボードデータの永続化."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from petatto_kanban.models import Board, Card, Column

DATA_FILE_NAME = "board.json"


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
        "description": card.description,
        "order": card.order,
        "created_at": _serialize_datetime(card.created_at),
        "updated_at": _serialize_datetime(card.updated_at),
    }


def _column_to_dict(column: Column) -> dict[str, Any]:
    return {
        "id": column.id,
        "name": column.name,
        "order": column.order,
        "cards": [_card_to_dict(card) for card in sorted(column.cards, key=lambda c: c.order)],
    }


def board_to_dict(board: Board) -> dict[str, Any]:
    """Board を JSON シリアライズ可能な dict に変換する."""
    return {
        "id": board.id,
        "name": board.name,
        "columns": [
            _column_to_dict(column)
            for column in sorted(board.columns, key=lambda col: col.order)
        ],
        "created_at": _serialize_datetime(board.created_at),
        "updated_at": _serialize_datetime(board.updated_at),
    }


def board_from_dict(data: dict[str, Any]) -> Board:
    """dict から Board を復元する."""
    columns: list[Column] = []
    for column_data in data.get("columns", []):
        cards = [
            Card(
                id=card["id"],
                title=card["title"],
                description=card.get("description", ""),
                order=card.get("order", 0),
                created_at=_parse_datetime(card["created_at"]),
                updated_at=_parse_datetime(card["updated_at"]),
            )
            for card in column_data.get("cards", [])
        ]
        cards.sort(key=lambda card: card.order)
        columns.append(
            Column(
                id=column_data["id"],
                name=column_data["name"],
                order=column_data.get("order", 0),
                cards=cards,
            )
        )
    columns.sort(key=lambda column: column.order)
    return Board(
        id=data["id"],
        name=data["name"],
        columns=columns,
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
