"""T-06: build_prompt 테스트."""

from celery_comment.prompt import build_prompt


class TestBuildPrompt:
    """T-06: 프롬프트 생성."""

    def test_prompt_contains_files(self) -> None:
        """T-06: 변경 파일 목록이 프롬프트에 포함."""
        prompt = build_prompt(["src/Main.java", "lib/Util.java"])
        assert "src/Main.java" in prompt
        assert "lib/Util.java" in prompt
        assert "search_codebase" in prompt
