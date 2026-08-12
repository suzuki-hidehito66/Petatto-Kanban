"""アプリケーションのエントリポイント."""

from petatto_kanban.app import run_app


def main() -> None:
    """GUI アプリケーションを起動する."""
    run_app()


if __name__ == "__main__":
    main()
