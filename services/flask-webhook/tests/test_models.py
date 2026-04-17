"""T-15: WebhookPayload 모델 테스트."""

from flask_webhook.models import PushCommit, WebhookPayload

from .conftest import make_push_payload


class TestWebhookPayload:
    """T-15: 정상 파싱."""

    def test_parse_push_payload(self) -> None:
        """T-15: Gitea push payload 정상 파싱."""
        data = make_push_payload(files=["src/Main.java", "lib/Util.java"])
        payload = WebhookPayload(**data)
        assert payload.ref == "refs/heads/main"
        assert payload.after == "abc12345deadbeef"
        assert payload.repo_full_name == "owner/repo"
        assert payload.clone_url == "http://gitea:3000/owner/repo.git"
        assert sorted(payload.all_changed_files()) == ["lib/Util.java", "src/Main.java"]

    def test_push_commit_defaults(self) -> None:
        """PushCommit 기본값 확인."""
        commit = PushCommit(id="abc", message="msg")
        assert commit.added == []
        assert commit.removed == []
        assert commit.modified == []

    def test_empty_commits(self) -> None:
        """커밋 없는 페이로드."""
        data = {
            "ref": "refs/heads/main",
            "after": "0000000",
            "repository": {"full_name": "a/b"},
            "commits": [],
        }
        payload = WebhookPayload(**data)
        assert payload.all_changed_files() == []
