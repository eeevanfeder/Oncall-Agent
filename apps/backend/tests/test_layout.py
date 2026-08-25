from tests.conftest import REPO_ROOT


def test_final_directories_exist() -> None:
    expected = [
        REPO_ROOT / "apps" / "backend",
        REPO_ROOT / "apps" / "frontend",
        REPO_ROOT / "packages" / "api-contracts",
        REPO_ROOT / "config",
        REPO_ROOT / "infra",
        REPO_ROOT / "scripts",
        REPO_ROOT / "openspec",
        REPO_ROOT / "docs",
        REPO_ROOT / "apps" / "backend" / "src" / "super_ai",
    ]
    missing = [str(path) for path in expected if not path.exists()]
    assert missing == []


def test_infra_has_no_app_container_files() -> None:
    forbidden = [
        REPO_ROOT / "app.Dockerfile",
        REPO_ROOT / "project.compose.json",
        REPO_ROOT / "infra" / "app.Dockerfile",
        REPO_ROOT / "infra" / "project.compose.json",
    ]
    existing = [str(path) for path in forbidden if path.exists()]
    assert existing == []
