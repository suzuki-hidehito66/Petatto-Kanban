"""モデルとストレージのテスト."""

from pathlib import Path

from petatto_kanban.models import Board, Card
from petatto_kanban.storage import board_from_dict, board_to_dict, load_board, save_board


def test_create_default_board_is_empty() -> None:
    board = Board.create_default()
    assert board.name == "My Board"
    assert board.cards == []


def test_save_and_load_board(tmp_path: Path) -> None:
    board = Board.create_default(name="Test Board")
    board.cards.append(Card(title="Write docs", x=50, y=60))

    data_path = tmp_path / "board.json"
    save_board(board, data_path)

    loaded = load_board(data_path)
    assert loaded.name == "Test Board"
    assert len(loaded.cards) == 1
    assert loaded.cards[0].title == "Write docs"
    assert loaded.cards[0].x == 50


def test_board_roundtrip_dict() -> None:
    board = Board.create_default()
    board.cards.append(Card(title="Implement feature", x=10, y=20))

    payload = board_to_dict(board)
    assert payload["schema_version"] == 3
    assert "description" not in payload["cards"][0]

    restored = board_from_dict(payload)

    assert restored.name == board.name
    assert len(restored.cards) == 1
    assert restored.cards[0].title == "Implement feature"
    assert restored.cards[0].x == 10


def test_load_legacy_card_with_description_ignored() -> None:
    legacy = {
        "schema_version": 2,
        "id": "board-1",
        "name": "Legacy",
        "created_at": "2026-08-12T10:00:00+00:00",
        "updated_at": "2026-08-12T10:00:00+00:00",
        "cards": [
            {
                "id": "card-1",
                "title": "Old task",
                "description": "drop me",
                "x": 10,
                "y": 20,
                "created_at": "2026-08-12T10:00:00+00:00",
                "updated_at": "2026-08-12T10:00:00+00:00",
            }
        ],
    }
    board = board_from_dict(legacy)
    assert board.cards[0].title == "Old task"
    resaved = board_to_dict(board)
    assert "description" not in resaved["cards"][0]


def test_load_missing_file_returns_default(tmp_path: Path) -> None:
    board = load_board(tmp_path / "missing.json")
    assert board.name == "My Board"
    assert board.cards == []


def test_migrate_legacy_columns_format() -> None:
    legacy = {
        "id": "board-1",
        "name": "Legacy",
        "created_at": "2026-08-12T10:00:00+00:00",
        "updated_at": "2026-08-12T10:00:00+00:00",
        "columns": [
            {
                "id": "col-1",
                "name": "To Do",
                "order": 0,
                "cards": [
                    {
                        "id": "card-1",
                        "title": "Old task",
                        "description": "",
                        "order": 0,
                        "created_at": "2026-08-12T10:00:00+00:00",
                        "updated_at": "2026-08-12T10:00:00+00:00",
                    }
                ],
            }
        ],
    }
    board = board_from_dict(legacy)
    assert len(board.cards) == 1
    assert board.cards[0].title == "Old task"
    assert board.cards[0].x == 80
