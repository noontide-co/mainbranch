"""Allow ``python -m mb`` to run the Typer app."""

from __future__ import annotations

from mb.cli import app


def main() -> None:
    """Entrypoint mirror of the ``mb`` console script."""
    app()


if __name__ == "__main__":
    main()
