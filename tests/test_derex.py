# -*- coding: utf-8 -*-
"""Tests for `derex.runner.cli` module."""

from click.testing import CliRunner
from derex.runner.project import Project
from itertools import repeat
from pathlib import Path
from types import SimpleNamespace

import os
import pytest
import traceback


MINIMAL_PROJ = Path(__file__).with_name("fixtures") / "minimal"
COMPLETE_PROJ = Path(__file__).with_name("fixtures") / "complete"
runner = CliRunner(mix_stderr=False)


@pytest.mark.slowtest
def test_derex_build(workdir, sys_argv):
    from derex.runner.cli import derex
    from derex.runner.ddc import ddc_project

    with workdir(COMPLETE_PROJ):
        result = runner.invoke(derex, ["compile-theme"])
        assert_result_ok(result)

        with sys_argv(["ddc-project", "config"]):
            ddc_project()
        assert Project().name in result.output
        assert os.path.isdir(Project().root / ".derex")


@pytest.mark.slowtest
def test_derex_reset_mysql(sys_argv, mocker, workdir):
    """Test the open edx ironwood docker compose shortcut."""
    from derex.runner.cli import derex
    from derex.runner.ddc import ddc_services

    mocker.patch("derex.runner.ddc.check_services", return_value=True)
    client = mocker.patch("derex.runner.docker.client")
    client.containers.get.return_value.exec_run.side_effect = [
        SimpleNamespace(exit_code=-1)
    ] + list(repeat(SimpleNamespace(exit_code=0), 10))

    with sys_argv(["ddc-services", "up", "-d"]):
        ddc_services()
    with workdir(MINIMAL_PROJ):
        result = runner.invoke(derex, ["reset-mysql"])
    assert_result_ok(result)
    assert result.exit_code == 0


def test_derex_runmode(testproj):
    from derex.runner.cli import derex

    with testproj:
        result = runner.invoke(derex, ["runmode"])
        assert result.exit_code == 0, result.output
        assert result.output == "debug\n"
        # Until this PR is merged we can't peek into `.stderr`
        # https://github.com/pallets/click/pull/1194
        assert result.stderr_bytes == b""

        result = runner.invoke(derex, ["runmode", "aaa"])
        assert result.exit_code == 2, result.output
        assert "Usage:" in result.stderr

        result = runner.invoke(derex, ["runmode", "production"])
        assert result.exit_code == 0, result.output
        assert "debug → production" in result.stderr_bytes.decode("utf8")

        result = runner.invoke(derex, ["runmode", "production"])
        assert result.exit_code == 0, result.output
        assert "already production" in result.stderr_bytes.decode("utf8")

        result = runner.invoke(derex, ["runmode"])
        assert result.exit_code == 0, result.output
        assert result.output == "production\n"
        assert result.stderr_bytes == b""


def test_derex_runmode_wrong(testproj):
    from derex.runner.cli import derex

    with testproj:
        project = Project()
        # Use low level API to inject invalid value
        project._set_status("runmode", "garbage")

        result = runner.invoke(derex, ["runmode"])
        # Ensure presence of error message
        assert "not valid" in result.stderr


def assert_result_ok(result):
    """Makes sure the click script exited on purpose, and not by accident
    because of an exception.
    """
    if not isinstance(result.exc_info[1], SystemExit):
        tb_info = "\n".join(traceback.format_tb(result.exc_info[2]))
        assert result.exit_code == 0, tb_info
