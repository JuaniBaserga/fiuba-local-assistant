from __future__ import annotations

from unittest.mock import patch

from fiuba_local import cli


def test_cli_dispatches_core_command():
    with patch.object(cli.core_commands, "run_stats", return_value=7) as command:
        with patch("sys.argv", ["fiuba-local", "stats"]):
            assert cli.main() == 7
    command.assert_called_once()


def test_cli_dispatches_semantic_command():
    with patch.object(cli.semantic_commands, "run_semantic_stats", return_value=8) as command:
        with patch("sys.argv", ["fiuba-local", "semantic", "stats"]):
            assert cli.main() == 8
    command.assert_called_once()


def test_cli_dispatches_study_command(tmp_path):
    with patch.object(cli.study_commands, "run_study_init", return_value=9) as command:
        with patch(
            "sys.argv",
            [
                "fiuba-local",
                "study",
                "init",
                "--dates-file",
                str(tmp_path / "dates.json"),
                "--state-file",
                str(tmp_path / "state.json"),
            ],
        ):
            assert cli.main() == 9
    command.assert_called_once()
