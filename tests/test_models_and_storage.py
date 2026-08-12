"""モデルとストレージのテスト."""

from pathlib import Path

from petatto_kanban.models import Board, Card
from petatto_kanban.storage import board_from_dict, board_to_dict, load_board, save_board


def test_create_default_board_has_three_columns() -> None:
    board = Board.create_default()
    assert board.name == "My Board"
    assert len(board.columns) == 3
    assert [column.name for column in board.columns] == ["To Do", "In Progress", "Done"]


def test_save_and_load_board(tmp_path: Path) -> None:
    board = Board.create_default(name="Test Board")
    column = board.columns[0]
    column.cards.append(Card(title="Write docs", order=0))

    data_path = tmp_path / "board.json"
    save_board(board, data_path)

    loaded = load_board(data_path)
    assert loaded.name == "Test Board"
    assert len(loaded.columns[0].cards) == 1
    assert loaded.columns[0].cards[0].title == "Write docs"


def test_board_roundtrip_dict() -> None:
    board = Board.create_default()
    board.columns[1].cards.append(Card(title="Implement feature", description="Details"))

    restored = board_from_dict(board_to_dict(board))

    assert restored.name == board.name
    assert len(restored.columns) == len(board.columns)
    assert restored.columns[1].cards[0].title == "Implement feature"
    assert restored.columns[1].cards[0].description == "Details"


def test_load_missing_file_returns_default(tmp_path: Path) -> None:
    board = load_board(tmp_path / "missing.json")
    assert board.name == "My Board"
    assert len(board.columns) == 3
