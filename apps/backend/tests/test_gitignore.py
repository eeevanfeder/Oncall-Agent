import subprocess
from pathlib import Path

from tests.conftest import REPO_ROOT

MUST_IGNORE = [
    "config/project.json",
    "config/user.project.json",
    ".env",
    ".env.local",
    ".idea/workspace.xml",
    ".venv/bin/python",
    "node_modules/pkg/index.js",
    "dist/index.js",
    "coverage/lcov.info",
    ".cache/tmp",
    "docs/.vitepress/cache/foo",
    "docs/.vitepress/dist/index.html",
    "apps/backend/var/data.db",
    "tmp.sqlite",
    "app.log",
]

MUST_TRACK = [
    "config/project.template.json",
    "config/user.project.template.json",
]


def _check_ignore(relpath: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", relpath],
        cwd=REPO_ROOT,
        check=False,
    )
    return result.returncode == 0


def test_sensitive_and_generated_paths_are_ignored() -> None:
    not_ignored = [path for path in MUST_IGNORE if not _check_ignore(path)]
    assert not_ignored == []


def test_templates_are_not_ignored() -> None:
    ignored = [path for path in MUST_TRACK if _check_ignore(path)]
    assert ignored == []
    for relpath in MUST_TRACK:
        assert (REPO_ROOT / Path(relpath)).is_file()
