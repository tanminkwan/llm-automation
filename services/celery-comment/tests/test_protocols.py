"""T-10: Protocol 만족 테스트."""

from .conftest import FakeAgent, FakeGitClient


class TestProtocols:
    """T-10: Fake 구현이 Protocol 을 만족하는지 확인."""

    def test_fake_git_client_satisfies_protocol(self) -> None:
        """FakeGitClient → GitClient Protocol."""
        from celery_comment.protocols import GitClient

        client: GitClient = FakeGitClient()
        assert hasattr(client, "clone")
        assert hasattr(client, "add_commit_push")

    def test_fake_agent_satisfies_protocol(self) -> None:
        """FakeAgent → AgentExecutor Protocol."""
        agent = FakeAgent()
        assert hasattr(agent, "run")
