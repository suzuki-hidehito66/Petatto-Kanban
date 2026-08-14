"""他アプリ判定のテスト."""

from unittest.mock import patch


def test_process_id_for_hwnd_rejects_empty() -> None:
    from petatto_kanban.display.win32_user32 import process_id_for_hwnd

    assert process_id_for_hwnd(None) is None
    assert process_id_for_hwnd(0) is None


def test_is_foreign_app_foreground_false_on_non_windows() -> None:
    with patch("petatto_kanban.display.foreign_app.is_windows", return_value=False):
        from petatto_kanban.display.foreign_app import is_foreign_app_foreground

        assert is_foreign_app_foreground() is False


def test_is_foreign_app_foreground_compares_process_id() -> None:
    with (
        patch("petatto_kanban.display.foreign_app.is_windows", return_value=True),
        patch("petatto_kanban.display.foreign_app.os.getpid", return_value=1000),
        patch(
            "petatto_kanban.display.win32_user32.foreground_process_id",
            return_value=2000,
        ),
    ):
        from petatto_kanban.display.foreign_app import is_foreign_app_foreground

        assert is_foreign_app_foreground() is True

    with (
        patch("petatto_kanban.display.foreign_app.is_windows", return_value=True),
        patch("petatto_kanban.display.foreign_app.os.getpid", return_value=1000),
        patch(
            "petatto_kanban.display.win32_user32.foreground_process_id",
            return_value=1000,
        ),
    ):
        from petatto_kanban.display.foreign_app import is_foreign_app_foreground

        assert is_foreign_app_foreground() is False


def test_is_foreign_app_under_cursor_false_on_non_windows() -> None:
    with patch("petatto_kanban.display.foreign_app.is_windows", return_value=False):
        from petatto_kanban.display.foreign_app import is_foreign_app_under_cursor

        assert is_foreign_app_under_cursor() is False


def test_is_foreign_app_under_cursor_compares_process_id() -> None:
    with (
        patch("petatto_kanban.display.foreign_app.is_windows", return_value=True),
        patch("petatto_kanban.display.foreign_app.os.getpid", return_value=1000),
        patch(
            "petatto_kanban.display.win32_user32.cursor_window_process_id",
            return_value=2000,
        ),
    ):
        from petatto_kanban.display.foreign_app import is_foreign_app_under_cursor

        assert is_foreign_app_under_cursor() is True

    with (
        patch("petatto_kanban.display.foreign_app.is_windows", return_value=True),
        patch("petatto_kanban.display.foreign_app.os.getpid", return_value=1000),
        patch(
            "petatto_kanban.display.win32_user32.cursor_window_process_id",
            return_value=1000,
        ),
    ):
        from petatto_kanban.display.foreign_app import is_foreign_app_under_cursor

        assert is_foreign_app_under_cursor() is False


def test_is_any_mouse_button_down_false_on_non_windows() -> None:
    with patch("petatto_kanban.display.mouse_buttons.is_windows", return_value=False):
        from petatto_kanban.display.mouse_buttons import is_any_mouse_button_down

        assert is_any_mouse_button_down() is False


def test_is_foreign_pointer_press_requires_button_and_foreign_window() -> None:
    from petatto_kanban.display.foreign_app import is_foreign_pointer_press

    with (
        patch(
            "petatto_kanban.display.foreign_app.is_any_mouse_button_down",
            return_value=True,
        ),
        patch(
            "petatto_kanban.display.foreign_app.is_foreign_app_under_cursor",
            return_value=True,
        ),
    ):
        assert is_foreign_pointer_press() is True

    with (
        patch(
            "petatto_kanban.display.foreign_app.is_any_mouse_button_down",
            return_value=False,
        ),
        patch(
            "petatto_kanban.display.foreign_app.is_foreign_app_under_cursor",
            return_value=True,
        ),
    ):
        assert is_foreign_pointer_press() is False

    with (
        patch(
            "petatto_kanban.display.foreign_app.is_any_mouse_button_down",
            return_value=True,
        ),
        patch(
            "petatto_kanban.display.foreign_app.is_foreign_app_under_cursor",
            return_value=False,
        ),
    ):
        assert is_foreign_pointer_press() is False


def test_is_foreign_pointer_press_true_when_foreign_window_is_moved() -> None:
    from petatto_kanban.display.foreign_app import is_foreign_pointer_press

    with (
        patch("petatto_kanban.display.foreign_app.is_windows", return_value=True),
        patch("petatto_kanban.display.foreign_app.os.getpid", return_value=1000),
        patch(
            "petatto_kanban.display.win32_user32.move_size_process_id",
            return_value=2000,
        ),
        patch(
            "petatto_kanban.display.foreign_app.is_any_mouse_button_down",
            return_value=False,
        ),
        patch(
            "petatto_kanban.display.foreign_app.is_foreign_app_under_cursor",
            return_value=False,
        ),
    ):
        assert is_foreign_pointer_press() is True


def test_is_foreign_pointer_press_true_when_foreign_app_has_capture() -> None:
    from petatto_kanban.display.foreign_app import is_foreign_pointer_press

    with (
        patch("petatto_kanban.display.foreign_app.is_windows", return_value=True),
        patch("petatto_kanban.display.foreign_app.os.getpid", return_value=1000),
        patch(
            "petatto_kanban.display.win32_user32.move_size_process_id",
            return_value=None,
        ),
        patch(
            "petatto_kanban.display.win32_user32.capture_process_id",
            return_value=2000,
        ),
        patch(
            "petatto_kanban.display.foreign_app.is_any_mouse_button_down",
            return_value=True,
        ),
        patch(
            "petatto_kanban.display.foreign_app.is_foreign_app_under_cursor",
            return_value=False,
        ),
    ):
        assert is_foreign_pointer_press() is True


def test_is_foreign_window_being_moved_false_on_non_windows() -> None:
    with patch("petatto_kanban.display.foreign_app.is_windows", return_value=False):
        from petatto_kanban.display.foreign_app import is_foreign_window_being_moved

        assert is_foreign_window_being_moved() is False
