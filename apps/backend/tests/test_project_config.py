import json
import os
from pathlib import Path

import pytest

from super_ai.project_config import load_project_config


def test_user_config_deep_merges_nested_fields(tmp_path: Path) -> None:
    project = {
        "frontend": {"title": "Base", "apiBaseUrl": "http://base", "theme": "light"},
        "llm": {"provider": "openai", "apiKey": "base-key"},
    }
    user = {
        "frontend": {"title": "User"},
        "llm": {"apiKey": "user-key"},
    }
    project_path = tmp_path / "project.json"
    user_path = tmp_path / "user.project.json"
    project_path.write_text(json.dumps(project), encoding="utf-8")
    user_path.write_text(json.dumps(user), encoding="utf-8")

    loaded = load_project_config(project_path=project_path, user_path=user_path)

    assert loaded["frontend"]["title"] == "User"
    assert loaded["frontend"]["apiBaseUrl"] == "http://base"
    assert loaded["frontend"]["theme"] == "light"
    assert loaded["llm"]["provider"] == "openai"
    assert loaded["llm"]["apiKey"] == "user-key"


def test_missing_files_are_empty_objects(tmp_path: Path) -> None:
    loaded = load_project_config(config_dir=tmp_path)
    assert loaded == {}


def test_does_not_read_os_environment_as_project_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project_path = tmp_path / "project.json"
    user_path = tmp_path / "user.project.json"
    project_path.write_text(json.dumps({"frontend": {"title": "FromJson"}}), encoding="utf-8")
    user_path.write_text("{}", encoding="utf-8")

    monkeypatch.setenv("SUPER_AI_TITLE", "FromEnv")
    monkeypatch.setenv("frontend_title", "FromEnv")
    monkeypatch.setenv("TITLE", "FromEnv")

    loaded = load_project_config(project_path=project_path, user_path=user_path)
    assert loaded == {"frontend": {"title": "FromJson"}}
    dumped = json.dumps(loaded)
    assert "FromEnv" not in dumped
    assert os.environ["SUPER_AI_TITLE"] == "FromEnv"
