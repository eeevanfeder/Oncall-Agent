from tests.conftest import REPO_ROOT

FORBIDDEN_HISTORY_REWRITE = ("filter-repo", "filter_repo", "push --force", "git push -f")


def test_docs_do_not_recommend_history_rewrite() -> None:
    roots = [
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "README.md",
        REPO_ROOT / "infra" / "README.md",
        REPO_ROOT / "scripts",
        REPO_ROOT / "apps" / "backend" / "README.md",
        REPO_ROOT / "apps" / "frontend" / "README.md",
        REPO_ROOT / "packages" / "api-contracts" / "README.md",
        REPO_ROOT / "docs" / "README.md",
        REPO_ROOT / "docs" / "index.md",
    ]
    hits: list[str] = []
    for path in roots:
        if path.is_dir():
            files = list(path.rglob("*"))
        elif path.is_file():
            files = [path]
        else:
            continue
        for file in files:
            if not file.is_file():
                continue
            text = file.read_text(encoding="utf-8").lower()
            for token in FORBIDDEN_HISTORY_REWRITE:
                if token in text:
                    hits.append(f"{file.relative_to(REPO_ROOT)}:{token}")
    assert hits == []


def test_infra_readme_locks_compose_boundary() -> None:
    text = (REPO_ROOT / "infra" / "README.md").read_text(encoding="utf-8")
    for token in ("etcd", "MinIO", "Milvus", "Attu", "Alertmanager"):
        assert token in text
    assert "主机" in text
