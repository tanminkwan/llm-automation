"""T-07~T-10: DiffEngine 테스트."""

from configaudit_mcp.diff_engine import DiffEngine
from configaudit_mcp.models import EnvConfig


class TestDiffBeforeAfter:
    """T-07: 변경 있음, T-08: 변경 없음."""

    def test_has_changes(self) -> None:
        """T-07: before≠after → has_changes=True + diff 텍스트."""
        engine = DiffEngine()
        config = EnvConfig(env="dev", before="Listen 80\n", after="Listen 8080\n")
        result = engine.diff_before_after(config)
        assert result.has_changes is True
        assert result.label == "dev:before→after"
        assert "---" in result.diff
        assert "+++" in result.diff
        assert "-Listen 80" in result.diff
        assert "+Listen 8080" in result.diff

    def test_no_changes(self) -> None:
        """T-08: before==after → has_changes=False."""
        engine = DiffEngine()
        config = EnvConfig(env="stage", before="Listen 80\n", after="Listen 80\n")
        result = engine.diff_before_after(config)
        assert result.has_changes is False
        assert result.diff == ""
        assert result.label == "stage:before→after"


class TestDiffCrossEnv:
    """T-09: 환경 간 차이 있음, T-10: 환경 간 동일."""

    def test_cross_env_diff(self) -> None:
        """T-09: 두 환경의 after 다름."""
        engine = DiffEngine()
        left = EnvConfig(env="dev", before="", after="Listen 80\n")
        right = EnvConfig(env="stage", before="", after="Listen 8080\n")
        result = engine.diff_cross_env(left, right)
        assert result.has_changes is True
        assert result.label == "after:dev↔stage"
        assert "-Listen 80" in result.diff
        assert "+Listen 8080" in result.diff

    def test_cross_env_same(self) -> None:
        """T-10: 두 환경의 after 동일."""
        engine = DiffEngine()
        left = EnvConfig(env="dev", before="", after="Listen 80\n")
        right = EnvConfig(env="stage", before="", after="Listen 80\n")
        result = engine.diff_cross_env(left, right)
        assert result.has_changes is False
        assert result.diff == ""
        assert result.label == "after:dev↔stage"
