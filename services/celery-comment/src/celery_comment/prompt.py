"""Agent 프롬프트 빌더."""

from __future__ import annotations


def build_prompt(changed_files: list[str]) -> str:
    """AgentRunner 에 전달할 프롬프트 생성.

    RAG MCP 의 search_codebase 도구를 활용하여
    변경된 Java 파일에 적절한 주석을 추가하도록 지시.
    """
    file_list = "\n".join(f"- {f}" for f in changed_files)
    return (
        "다음 Java 파일에 적절한 주석을 추가해 주세요.\n"
        "search_codebase 도구를 사용하여 유사한 코드 패턴의 주석을 검색하고,\n"
        "그 스타일에 맞춰 클래스/메서드/복잡한 로직에 한국어 주석을 삽입하세요.\n"
        "변경 후 파일을 저장하세요.\n\n"
        f"변경 대상 파일:\n{file_list}"
    )
